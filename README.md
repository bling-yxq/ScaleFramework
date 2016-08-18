#ScaleFramework
Main：
	Web服务
		写config文件、monitorQ的队列要修改
	指定URI
	创建excutor
		MonitorExecutor（MonitorQueue一个app对应一个task）framemessage通知scale
		ScalerExecutor（ScalerQueue一个scale任务对应一个task）
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

	def getmaxtasknum(offer)
		//一个offer可以提供多少task运行

	def resourceoffers()
		if monitorQ==empty || scalerQ==empty
			nothing to do
		for offer in offers:
			tasks=[ ]
			//monitor的task优先，有的task要kill掉，modify标志位
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