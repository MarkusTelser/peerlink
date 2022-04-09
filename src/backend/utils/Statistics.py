from datetime import datetime

class Statistics:
    def __init__(self, conf):
        self._total_downloaded = conf.total_downloaded
        self._total_uploaded = conf.total_uploaded
        self.total_ratio = conf.total_uploaded / conf.total_downloaded
        
        self.session_downloaded = 0
        self.session_uploaded = 0
        self.session_ratio = 0

        self._start_date = datetime.now()
        self._total_time_running = conf.total_time_running

        self.program_running_since = conf.program_running_since  
        self.program_opened = conf.program_opened + 1   

    @property
    def total_downloaded(self):
        return self._total_downloaded + self.session_downloaded
    
    @property
    def total_uploaded(self):
        return self._total_uploaded + self.session_uploaded

    @property
    def total_time_running(self):
        return self._total_time_running + self.session_time_running

    def update(self, swarm_list):
        self.session_downloaded += 10 
        self.session_uploaded += 10
        
        self.total_ratio = self.total_uploaded / self.total_downloaded
        self.session_ratio = self.session_uploaded / self.session_downloaded

        self.session_time_running = (datetime.now() - self._start_date).seconds
