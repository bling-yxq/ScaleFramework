#ScaleFramework

环境要求

	mesos-slave mesos-master zookeeper
	python依赖 web.py protobuf

当前完成

	webexecutor的最简单访问task，只能访问页面，没有其他功能。

目前有几个问题没有解决

	开启framework的时候经常会失败，失败好几次，好像是端口占用问题
	uri指定以后，开启http服务，仍然不能获取代码
	在本机访问本机ip地址的时候不能访问，就是http服务用curl也不能获取，但是其他机器可以访问

	在state改变的时候需要做处理，fail的时候需要restart一下task。
	随机一个端口
	结合haproxy使用，现在只能指定slave的地址和端口才能访问，最好能自动配置
	对于rules的同步还不知道怎么做，比如fail之后在另一台机器上起，该怎么同步rules

程序结构

Main：

	指定URI
	创建excutor
		MonitorExecutor（MonitorQueue一个app对应一个task）framemessage通知scale
		ScalerExecutor（ScalerQueue一个scale任务对应一个task）
		webExecutor
	创建scheduler
	创建framework

Class scalerscheduler(scheduler):

	def __init__(self, MonitorExecutor, ScaleExecutor, …)

	def registed()

	def makeMonitorTask( self, …, offer )
		task.data=appname，rules…
		task.slaveid…
		add cpu mem

	def makeScaleTask()
		同上

	def makewebTask()
		只创建一个task，当task fail的时候要重新创建

	def getmaxtasknum(offer)
		//一个offer可以提供多少task运行

	def resourceoffers()
		if monitorQ==empty || scalerQ==empty
			nothing to do
		for offer in offers:
			tasks=[ ]
			//优先级webexecutor>monitorexecutor>scalerexecutor 有的task要kill掉，modify标志位
			Maxtasknum=self.getmaxtasknum(offer)
			For i in Maxtasknum && monitorQ.hasnotsubmit()	//还有没有submit的任务
			(app,rules,…)=monitorQ.getleft()	//get之后要修改标志位，标明已经subumit了这个任务
			Task=self.makeMonitorTask(app,rules…,offer)
			Tasks.append(task)
				//scale的task用剩下的offer
				…
			Driver.launchTasks(offer.id, tasks)
			//多余的offer释放
			Declineoffer()