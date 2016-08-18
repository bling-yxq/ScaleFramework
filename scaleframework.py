import json
import os
import signal
import sys
import time
from threading import Thread

try:
    from mesos.native import MesosExecutorDriver, MesosSchedulerDriver
    from mesos.interface import Executor, Scheduler
    from mesos.interface import mesos_pb2
except ImportError:
    from mesos import Executor, MesosExecutorDriver, MesosSchedulerDriver, Scheduler
    import mesos_pb2

LEADING_ZEROS_COUNT = 5  # appended to task ID to facilitate lexicographical order

class ScalerScheduler(Scheduler):
    TASK_CPUS = 0.1
    TASK_MEM = 32
    def __init__(self, webExecutor):
        self.webExecutor = webExecutor
        self.tasksCreated = 0
        self.webserveron = False

    def makeTaskPrototype(self, offer):
        task = mesos_pb2.TaskInfo()
        tid = self.tasksCreated
        self.tasksCreated += 1
        task.task_id.value = str(tid).zfill(LEADING_ZEROS_COUNT)
        task.slave_id.value = offer.slave_id.value
        cpus = task.resources.add()
        cpus.name = "cpus"
        cpus.type = mesos_pb2.Value.SCALAR
        cpus.scalar.value = self.TASK_CPUS
        mem = task.resources.add()
        mem.name = "mem"
        mem.type = mesos_pb2.Value.SCALAR
        mem.scalar.value = self.TASK_MEM
        return task

    def makeWebTask(self, offer):
        task = self.makeTaskPrototype(offer)
        task.name = "web task %s" % task.task_id.value
        task.task_id.value += "-web"
        task.executor.MergeFrom(self.webExecutor)
        task.data="8888"
        return task

    def registered(self, driver, frameworkId, masterInfo):
        print "Registered with framework ID [%s]" % frameworkId.value

    def statusUpdate(self, driver, status):
        print "received status update:{}".format(status)

    def resourceOffers(self, driver, offers):
        for offer in offers:
            tasks = []
            print "offer:{}".format(offer)
            if not self.webserveron:
                print "webserver on"
                offer_cpu = 0
                offer_mem = 0
                for resource in offer.resources:
                    if resource.name == "cpus":
                        offer_cpu = resource.scalar.value
                    if resource.name == "mem":
                        offer_mem = resource.scalar.value
                if offer_mem >= self.TASK_MEM and offer_cpu >= self.TASK_CPUS:
                    offer_cpu -= self.TASK_CPUS
                    offer_mem -= self.TASK_MEM
                    task = self.makeWebTask(offer)
                    self.webserveron = True
                    tasks.append(task)

            if tasks:
                driver.launchTasks(offer.id, tasks)


    def reregistered(self, driver, masterInfo):
        pass

    def error(self, driver, message):
        pass

    def executorLost(self, driver, executorId, slaveId, status):
        pass

    def slaveLost(self, driver, slaveId):
        pass

    def disconnected(self, driver):
        pass

    def frameworkMessage(self, driver, executorId, slaveId, data):
        pass

def hard_shutdown():  
    driver.stop()

if __name__ == "__main__":

    baseURI = "20.26.25.117:2222/ScaleFramework"
    uris = [ "web_executor.py",
             "rules.json"]
    uris = [os.path.join(baseURI, uri) for uri in uris]

    webExecutor = mesos_pb2.ExecutorInfo()
    webExecutor.executor_id.value = "web-executor"
    webExecutor.command.value = "python web_executor.py"

    for uri in uris:
        uri_proto = webExecutor.command.uris.add()
        uri_proto.value = uri
        uri_proto.extract = False

    webExecutor.name = "Web"

    framework = mesos_pb2.FrameworkInfo()
    framework.user = "" # Have Mesos fill in the current user.
    framework.name = "SCALERFW"
    framework.role = "*"
    framework.checkpoint = False
    framework.failover_timeout = 0.0

    scaler = ScalerScheduler(webExecutor)
    mesosURL = "zk://20.26.25.117:2181,20.26.25.117:2182,20.26.25.117:2183/mesos" # IP / hostname of mesos master
    driver = MesosSchedulerDriver(scaler, framework, mesosURL)

    # driver.run() blocks; we run it in a separate thread
    def run_driver_async():
        status = 0 if driver.run() == mesos_pb2.DRIVER_STOPPED else 1
        driver.stop()
        sys.exit(status)
    framework_thread = Thread(target = run_driver_async, args = ())
    framework_thread.start()

    print "(Listening for Ctrl-C)"
    signal.signal(signal.SIGINT, hard_shutdown)
    while framework_thread.is_alive():
        time.sleep(1)