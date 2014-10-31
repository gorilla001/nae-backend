from containers import ContainerController
from images import ImageController
from projects import ProjectController
from users import UserController
from hgs import HgController
from misc   import MiscController

import routes
import routes.middleware
import webob.dec

class Router (object):
    def __init__(self):

        self.mapper=routes.Mapper()
        self.container_controller=ContainerController()
        self.image_controller=ImageController()
        self.project_controller=ProjectController()
        self.user_controller=UserController()
        self.misc_controller=MiscController()
        self.hg_controller=HgController()

        #self.mapper.redirect("","/")
        
        self.mapper.connect('/containers',
        		controller=self.container_controller,
        		action='index',
        		conditions={'method':['GET']},
        )
        self.mapper.connect('/containers/{container_id}',
        		controller=self.container_controller,
        		action='delete',
        		conditions={'method':['DELETE']},
        )
        
        self.mapper.connect('/containers/{container_id}',
        		controller=self.container_controller,
        		action='show',
        		condition={'method':['GET']},
        )
        
        self.mapper.connect('/containers/{container_id}',
        		controller=self.container_controller,
        		action='inspect',
        		conditions={'method':['GET']},
        )

        self.mapper.connect('/containers/{container_id}/stop',
        		controller=self.container_controller,
        		action='stop',
        		conditions={'method':['POST']},
        )
        self.mapper.connect('/containers/{container_id}/start',
        		controller=self.container_controller,
        		action='start',
        		conditions={'method':['POST']},
        )
        self.mapper.connect('/containers/{container_id}/reboot',
        		controller=self.container_controller,
        		action='reboot',
        		conditions={'method':['POST']},
        )
        self.mapper.connect('/containers/{container_id}/commit',
        		controller=self.container_controller,
        		action='commit',
        		conditions={'method':['POST']},
        )
        
        self.mapper.connect('/containers/{container_id}/destroy',
        		controller=self.container_controller,
        		action='destroy',
        		conditions={'method':['POST']},
        )

        
        self.mapper.connect('/containers',
        		controller=self.container_controller,
        		action='create',
        		conditions={'method':['POST']},
        )
        
        self.mapper.connect('/images',
        		controller=self.image_controller,
        		action='index',
        		conditions={'method':['GET']},
        )
        self.mapper.connect('/images/{image_id}',
        		controller=self.image_controller,
        		action='show',
        		conditions={'method':['GET']},
        )
        self.mapper.connect('/images/{image_id}/inspect',
        		controller=self.image_controller,
        		action='inspect',
        		conditions={'method':['GET']},
        )
        
        self.mapper.connect('/images',
        		controller=self.image_controller,
        		action='create',
        		conditions={'method':['POST']},
        )
        
        self.mapper.connect('/images/{image_id}',
        		controller=self.image_controller,
        		action='delete',
        		conditions={'method':['DELETE']},
        )
	self.mapper.connect('/images/edit',
        		controller=self.image_controller,
        		action='edit',
        		conditions={'method':['POST']},
        )
	self.mapper.connect('/images/commit',
        		controller=self.image_controller,
        		action='commit',
        		conditions={'method':['POST']},
        )

        #file method
        self.mapper.connect('/files',
				controller=self.image_controller,
				action='index',
				conditions={'method':['GET']},
		)
        self.mapper.connect('/files/{file_id}',
				controller=self.image_controller,
				action='show',
				conditions={'method':['GET']},
		)
        self.mapper.connect('/files/{file_id}/modify',
				controller=self.image_controller,
				action='modify',
				conditions={'method':['GET']},
		)

        self.mapper.connect('/files',
				controller=self.image_controller,
				action='create',
				conditions={'method':['POST']},
		)
		
        self.mapper.connect('/files/{file_id}',
				controller=self.image_controller,
				action='delete',
				conditions={'method':['DELETE']},
		)

        self.mapper.connect('/projects',
				controller=self.project_controller,
				action='index',
				conditions={'method':['GET']},
		)

        self.mapper.connect('/projects',
				controller=self.project_controller,
				action='create',
				conditions={'method':['POST']},
		)

        self.mapper.connect('/projects/{id}',
				controller=self.project_controller,
				action='delete',
				conditions={'method':['DELETE']},
		)
        self.mapper.connect('/projects/{id}',
				controller=self.project_controller,
				action='show',
				conditions={'method':['GET']},
		)
        self.mapper.connect('/projects/{id}',
				controller=self.project_controller,
				action='update',
				conditions={'method':['PUT']},
		)


        self.mapper.connect('/users',
				controller=self.user_controller,
				action='index',
				conditions={'method':['GET']},
		)
        self.mapper.connect('/users',
				controller=self.user_controller,
				action='create',
				conditions={'method':['POST']},
		)

        self.mapper.connect('/users/{id}',
				controller=self.user_controller,
				action='delete',
				conditions={'method':['DELETE']},
		)

        self.mapper.connect('/hgs',
				controller=self.hg_controller,
				action='index',
				conditions={'method':['GET']},
		)
        self.mapper.connect('/hgs',
				controller=self.hg_controller,
				action='create',
				conditions={'method':['POST']},
		)

        self.mapper.connect('/hgs/{id}',
				controller=self.hg_controller,
				action='delete',
				conditions={'method':['DELETE']},
		)


        self.mapper.connect('/info',
				controller=self.misc_controller,
				action='info',
				condition={'method':['GET']},
		)

        self.mapper.connect('/version',
				controller=self.misc_controller,
				action='version',
				condition={'method':['GET']},
		)	
        self.mapper.connect('/events',
				controller=self.misc_controller,
				action='events',
				condition={'method':['GET']},
		)
        self.router=routes.middleware.RoutesMiddleware(self._dispatch,self.mapper)

    @classmethod
    def factory(cls,global_config,**local_config):
		return cls()
	
    @webob.dec.wsgify
    def __call__(self,req):
		return self.router

    @staticmethod
    @webob.dec.wsgify
    def _dispatch(req):
		match=req.environ['wsgiorg.routing_args'][1]
		if not match:
			return webob.Response('{"error" : "404 Not Found"}')
		app=match['controller']
		return app
