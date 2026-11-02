class Issue:
    
    def __init__(self, jobj:any=None):
        self.url:str = None
        self.creator:str = None
        self.labels:List[str] = []
        self.state:State = None
        self.assignees:List[str] = []
        self.title:str = None
        self.text:str = None
        self.number:int = -1
        self.created_date:datetime = None
        self.updated_date:datetime = None
        self.timeline_url:str = None
        self.events:List[Event] = []
        
        if jobj is not None:
            self.from_json(jobj)
    
    def from_json(self, jobj:any):
        self.url = jobj.get('url')
        self.creator = jobj.get('creator')
        self.labels = jobj.get('labels',[])
        self.state = State[jobj.get('state')]
        self.assignees = jobj.get('assignees',[])
        self.title = jobj.get('title')
        self.text = jobj.get('text')
        try:
            self.number = int(jobj.get('number','-1'))
        except:
            pass
        try:
            self.created_date = parser.parse(jobj.get('created_date'))
        except:
            pass
        try:
            self.updated_date = parser.parse(jobj.get('updated_date'))
        except:
            pass
        self.timeline_url = jobj.get('timeline_url')
        self.events = [Event(jevent) for jevent in jobj.get('events',[])]
