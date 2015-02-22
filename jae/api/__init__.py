from jae import wsgi
from jae.api import containers
from jae.api import images
from jae.api import projects
from jae.api import users
from jae.api import repos
import routes


class APIRouter(wsgi.Router):
    def __init__(self):
        self.mapper = routes.Mapper()
        self._setup_routes()
        super(APIRouter, self).__init__(self.mapper)

    def _setup_routes(self):
        """
        Set up routes use the correspoding resource.
        """

        self.mapper.resource('container', 'containers',
                             controller=containers.create_resource(),
                             member={'start': 'POST',
                                     'stop': 'POST',
                                     'reboot': 'POST',
                                     'commit': 'POST',
                                     'destroy': 'POST',
                                     'refresh': 'POST'})
        """The above commands establishes the following convention:
           >>> GET    /containers         => containers.index()
           >>> POST   /containers         => containers.create()
           >>> GET    /containers/new     => containers.new()
           >>> PUT    /containers/id      => containers.update(id)
           >>> DELETE /containers/id      => containers.delete(id)
           >>> GET    /containers/id      => containers.show(id)
           >>> GET    /containers/id/edit => containers.edit(id)
           >>> POST   /containers/id/start     => containers.start(id)
           >>> POST   /containers/id/stop      => containers.stop(id)
           >>> POST   /containers/id/reboot    => containers.reboot(id)
           >>> POST   /containers/id/commit    => containers.commit(id)
           >>> POST   /containers/id/destroy   => containers.destroy(id)
           >>> POST   /containers/id/refresh   => containers.refresh(id)
        """
        
        self.mapper.resource('image',
                             'images',
                             controller=images.create_resource(),
                             member={'destroy': 'POST'})

        self.mapper.connect('/images/commit',
                            controller=images.create_resource(),
                            action='commit',
                            conditions={'method': ['POST']})

        """The above commands establishes the following convention:
           >>> GET    /images      => images.index()
           >>> GET    /images/id   => images.show(id)
           >>> POST   /images      => images.create()
           >>> DELETE /images/id   => images.delete(id)
           >>> PUT    /images/id   => images.update(id)
           >>> GET    /images/new  => images.new()
           >>> GET    /images/id/edit => images.edit(id)
           >>> POST   /images/id/destroy => images.destroy(id)
           >>> POST   /images/commit/id => images.commit(id)
        """
        self.mapper.resource('project', 'projects',
                             controller=projects.create_resource())

        """The above commands establishes the following convention:
           >>> GET    /projects       => projects.index()
           >>> GET    /projects/id    => projects.show(id)
           >>> POST   /projects       => projects.create()
           >>> DELETE /projects/id    => projects.delete(id)
           >>> PUT    /projects/id    => projects.update(id)
           >>> GET    /projects/new   => projects.new()
        """
        self.mapper.resource('user', 'users',
                             controller=users.create_resource())

        """The above commands establishes the following convention:
           >>> GET    /users       => users.index()
           >>> GET    /users/id    => users.show(id)
           >>> POST   /users       => users.create()
           >>> DELETE /users/id    => users.delete(id)
           >>> PUT    /users/id    => users.update(id)
           >>> GET    /users/new   => users.new()
        """
        self.mapper.resource('repository', 'repos',
                             controller=repos.create_resource())

        """The above commands establishes the following convention:
           >>> GET    /repos       => repos.index()
           >>> GET    /repos/id    => repos.show(id)
           >>> POST   /repos       => repos.create()
           >>> DELETE /repos/id    => repos.delete(id)
           >>> PUT    /repos/id    => repos.update(id)
           >>> GET    /repos/new   => repos.new()
        """

