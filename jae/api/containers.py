import webob.exc
import requests
import uuid
import json

from jae import wsgi
from jae.common import log as logging
from jae.common.exception import ContainerLimitExceeded
from jae.common.response import Response, ResponseObject
from jae.common import quotas
from jae.common import cfg
from jae.common import timeutils
from jae.scheduler import scheduler
from jae.common import exception
from jae.common import client
from jae.base import Base

CONF = cfg.CONF

LOG = logging.getLogger(__name__)

QUOTAS = quotas.Quotas()

EMPTY_STRING = ""


class Controller(Base):
    def __init__(self):
        super(Controller, self).__init__()

        if not CONF.default_scheduler:
            self._scheduler = scheduler.SimpleScheduler()

        self.http = client.HTTPClient()

    def index(self, request):
        """
            List all containers on all container nodes according to `project_id`
            and `user_id`.

            This method returns a dictionary list and each dict contains the following keys:
                - id
                - uuid
                - name
                - repos
                - branch
                - image
                - project_id 
                - user_id 
                - network
                - created
                - status

            If no container found, a empty list will be returned.
        """
        containers = []

        project_id = request.GET.get('project_id',None)
        user_id = request.GET.get('user_id',None)

        query = self.db.get_containers(project_id, user_id)
        for item in query:
            container = {
                'id': item.id,
                'uuid': item.uuid,
                'name': item.name,
                'repos': item.repos,
                'branch': item.branch,
                'image_id': item.image_id,
                'project_id': item.project_id,
                'user_id': item.user_id,
                'network': item.fixed_ip,
                'created': timeutils.isotime(item.created),
                'status': item.status,
            }
            container.setdefault("image", "")
            """Get the image name and tag by the `image_id`.
               if the image not found, use the default."""
            image_id = item.image_id
            image_instance = self.db.get_image(image_id)
            if image_instance:
                image = "%s:%s" % (image_instance.name, image_instance.tag)
                container.update({"image": image})

            containers.append(container)
        return ResponseObject(containers)

    def show(self, request, id):
        """
        Show the container info according container's id.

        :params id: container's id

        This method returns a dictionary with following keys:
            - id
            - name
            - uuid
            - env
            - project_id
            - repos
            - branch
            - image_id
            - network
            - created
            - user_id
            - host_id
            - status
         
        If no container found, a empty dictionary will returned.
        """

        container = {}
        query = self.db.get_container(id)
        if query is not None:
            container = {
                'id': query.id,
                'name': query.name,
                'uuid': query.uuid,
                'env': query.env,
                'project_id': query.project_id,
                'repos': query.repos,
                'branch': query.branch,
                'image_id': query.image_id,
                'network': query.fixed_ip,
                'created': timeutils.isotime(query.created),
                'user_id': query.user_id,
                'host_id': query.host_id,
                'status': query.status,
            }

        return ResponseObject(container)


    def create(self, request, body=None):
        """
        Create container.
        """
        if not body:
            msg = "post request has no body?"
            LOG.error(msg)
            return webob.exc.HTTPBadRequest(explanation=msg)
        project_id = body.pop('project_id')
        if not project_id:
            msg = "project id must be provided."
            LOG.error(msg)
            return webob.exc.HTTPBadRequest(explanation=msg)

        image_id = body.pop('image_id')
        if image_id == "-1":
            msg = "invalid image id -1."
            LOG.error(msg)
            return web.exc.HttpBadRequest(explanation=msg)
        query = self.db.get_image(image_id)
        if not query:
            msg = "image id is invalid,no such image."
            LOG.error(msg)
            return webob.exc.HTTPBadRequest(explanation=msg)

        user_id = body.pop('user_id')
        if not user_id:
            msg = "user id must be provided."
            LOG.error(msg)
            return webob.exc.HTTPBadRequest(explanation=msg)

        limit = QUOTAS.containers or _CONTAINER_LIMIT
        query = self.db.get_containers(project_id, user_id)
        if len(query) >= limit:
            msg = 'container limit exceeded!!!'
            LOG.error(msg)
            return webob.exc.HTTPForbidden(explanation=msg)

        repos = body.pop('repos')
        if not repos:
            msg = "repos must be provided"
            LOG.error(msg)
            return webob.exc.HTTPBadRequest(explanaiton=msg)

        branch = body.pop('branch')
        if not branch:
            msg = "branch must be provided"
            LOG.error(msg)
            return webob.exc.HTTPBadRequest(explanaiton=msg)

        env = body.pop('env')
        if not env:
            msg = "env must be provided"
            LOG.error(msg)
            return webob.exc.HTTPBadRequest(explanation=msg)

        user_key = body.pop('user_key')
        if not user_key:
            user_key = EMPTY_STRING

        zone_id = body.pop('zone_id')
        if not zone_id:
            zone_id = 0

        app_type = body.pop('app_type')
        if not app_type:
            app_type = "php"

        maven_flags = body.pop("maven_flags")
        
        """Call the scheduler to decide which host the container will 
           be run on.
        """
        # TODO(nmg): This should be modified to use rpc call not function call. 
        try:
            instance = self._scheduler.run_instance(project_id,
                                                    user_id,
                                                    image_id,
                                                    repos,
                                                    branch,
                                                    app_type,
                                                    env,
                                                    user_key,
                                                    zone_id,
                                                    maven_flags)
        except exception.NoValidHost:
            raise

        return ResponseObject(instance)

    def delete(self, request, id):
        """
        Send delete `request` to remote server for deleting.
        if failed,excepiton will be occured.

        :param request: `wsgi.Request`
        :param id: container idenfier
        """
        container = self.db.get_container(id)
        if not container:
            return webob.exc.HTTPOk()

        host_id = container.host_id
        host = self.db.get_host(host_id)
        if not host:
            LOG.error("no such host %s" % host_id)
            return webob.exc.HTTPNotFound()

        host, port = host.host, host.port
        # FIXME: try to catch exceptions and dealing with it. 
        response = self.http.delete("http://%s:%s/v1/containers/%s" \
                                    % (host, port, id))

        return Response(response.status_code)

    def start(self, request, id):
        container = self.db.get_container(id)
        if not container:
            LOG.error("nu such container %s" % id)
            return webob.exc.HTTPNotFound()
        host = self.db.get_host(container.host_id)
        if not host:
            LOG.error("no such host")
            return webob.exc.HTTPNotFound()
        host, port = host.host, host.port

        response = self.http.post("http://%s:%s/v1/containers/%s/start" \
                                  % (host, port, id))

        return Response(response.status_code)

    def stop(self, request, id):
        """send stop request to remote host where container on."""
        container = self.db.get_container(id)
        if not container:
            LOG.error("nu such container %s" % id)
            return webob.exc.HTTPNotFound()

        host_id = container.host_id
        host = self.db.get_host(host_id)
        if not host:
            LOG.error("no such host")
            return webob.exc.HTTPNotFound()

        host, port = host.host, host.port
        response = self.http.post("http://%s:%s/v1/containers/%s/stop" \
                                  % (host, port, id))

        return Response(response.status_code)

    def reboot(self, request):
        pass

    def destroy(self, request, body):
        """send destroy request to remote host."""

        return NotImplementedError()

    def commit(self, request, body):
        """send commit request to remote host."""

        return NotImplementedError()

    def refresh(self, request, id):
        """
        Refresh code in container. refresh request will be 
        send to remote container server for refreshing.
        if send request failed,exception will occured.
        is it necessary to catch the exception? I don't
        know. 

        :param request: `wsgi.Request` object
        :param id     : container idenfier
        """
        """check if this container is really exists,
           otherwise return 404 not found"""

        container = self.db.get_container(id)
        if not container:
            LOG.error("nu such container %s" % id)
            return webob.exc.HTTPNotFound()

        """update container status"""

        """get host id from container info,
           if host id is None,return 404"""

        host_id = container.host_id
        if not host_id:
            LOG.error("container %s has no host_id" % id)
            return webob.exc.HTTPNotFound()

        """get host instance by `host_id`,
           if host instance is None,return 404"""
        host = self.db.get_host(host_id)
        if not host:
            LOG.error("no such host")
            return webob.exc.HTTPNotFound()

        """get ip address and port for host instance."""
        host, port = host.host, host.port


        """get data branch"""
        branch = request.GET.get('branch')
        """make post request to the host where container on."""
        # FIXME: exception shoud be catch?
        response = self.http.post("http://%s:%s/v1/containers/%s/refresh?branch=%s" \
                                  % (host, port, id,branch))

        return Response(response.status_code)

    def share(self, request, id, body):
        query = self.db.get_container(id)
        if not query:
            LOG.error("no such container %s" % id)
            return
        shared_id = uuid.uuid4().hex 
        origin_uuid = query.uuid
        name = query.name
        env = query.env
        project_id = query.project_id
        repos = query.repos
        branch = query.branch
        image_id = query.image_id
        host_id = query.host_id
        app_type = query.app_type
        origin_user_id = query.user_id
        shared_user_id = body.get("user_id")
        user_key = body.get("user_key")
        fixed_ip = query.fixed_ip

        """creating db entry for new container"""
        project = self.db.get_project(project_id)
        if not project:
            LOG.error("no such project %s" % project_id)
            return Response(404)
        self.db.add_container(dict(
            id=shared_id,
            uuid=origin_uuid,
            name=name,
            env=env,
            repos=repos,
            branch=branch,
            image_id=image_id,
            user_id=shared_user_id,
            host_id=host_id,
            app_type=app_type,
            fixed_ip=fixed_ip,
            status="sharing"),
            project=project)
      
        host_id = query.host_id
        if not host_id:
            LOG.error("container %s has no host_id" % id)
            return webob.exc.HTTPNotFound()

        """get host instance by `host_id`,
           if host instance is None,return 404"""
        host = self.db.get_host(host_id)
        if not host:
            LOG.error("no such host")
            return webob.exc.HTTPNotFound()

        """get ip address and port for host instance."""
        host, port = host.host, host.port
        data = {'shared_id': shared_id,
                'uuid': origin_uuid,
                'user_key': user_key,
                'origin_user': origin_user_id,
                'shared_user': shared_user_id} 
        headers={'content-type': 'application/json'}
        response = self.http.post("http://%s:%s/v1/containers/%s/share" \
                                 % (host,port,id),headers=headers,data=json.dumps(data))
        return Response(response.status_code)

def create_resource():
    return wsgi.Resource(Controller())
