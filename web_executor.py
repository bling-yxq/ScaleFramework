import web
import sys
from threading import Thread
import threading

try:
    from mesos.native import MesosExecutorDriver, MesosSchedulerDriver
    from mesos.interface import Executor, Scheduler
    from mesos.interface import mesos_pb2
except ImportError:
    from mesos import Executor, MesosExecutorDriver, MesosSchedulerDriver, Scheduler
    import mesos_pb2
 
urls = (
    '/', 'hello',
    '/test','test'
       )
 
class hello(object):
  def GET(self):
      return 'hello world'
 
class test(object):
    def POST(self):
        i = web.input()
        return i.info
      
class MyApplication(web.application):
    def run(self, port=8888, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))

class webExecutor(Executor):

    def registered(self, driver, executorInfo, frameworkInfo, slaveInfo):
        print "webExecutor registered"

    def reregistered(self, driver, slaveInfo):
        print "webExecutor reregistered"

    def disconnected(self, driver):
        print "webExecutor disconnected"

    def launchTask(self, driver, task):
        def run_task():
            print "Running render task %s" % task.task_id.value
            update = mesos_pb2.TaskStatus()
            update.task_id.value = task.task_id.value
            update.state = mesos_pb2.TASK_RUNNING
            driver.sendStatusUpdate(update)
            myport = task.data
            app = MyApplication(urls, globals())
            app.run(port=myport)

        thread = threading.Thread(target=run_task)
        thread.start()

    def killTask(self, driver, taskId):
      pass

    def frameworkMessage(self, driver, message):
      pass

    def shutdown(self, driver):
      pass

    def error(self, error, message):
      pass

if __name__ == "__main__":
    driver = MesosExecutorDriver(webExecutor())
    sys.exit(0 if driver.run() == mesos_pb2.DRIVER_STOPPED else 1)
