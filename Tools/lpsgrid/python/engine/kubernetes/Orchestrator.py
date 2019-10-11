
__all__ = ["Kubernetes"]

from Gaugi import Logger
from kubernetes import *
from pprint import pprint
from lpsgrid.engine.enumerations import StatusJob, status_job_toString


class Kubernetes(Logger):

  def __init__(self):

    import os
    # this is the current config LPS cluster yaml file
    config.load_kube_config(config_file=os.environ['SAPHYRA_PATH']+'/Tools/lpsgrid/data/lps_cluster.yaml')
    # Get the job batch api
    self._api = client.BatchV1Api()
    self._template_job_path = os.environ['SAPHYRA_PATH']+'/Tools/lpsgrid/data/job_template.yaml'


  def api(self):
    return self._api


  def getTemplate( self ):
    from benedict import benedict
    return dict(b.from_yaml(self._template_job_path))



  def status( self, name ):
    resp = self.api().read_namespaced_job_status( name=name, namespace='default' )
    if not resp.status.active is None:
      return StatusJob.RUNNING
    elif not resp.status.failed is None:
      return StatusJob.FAILED
    return StatusJob.DONE



  def create( self, path ):

    pprint(d)
    # Send the job configuration to cluster kube server
    resp = self.api().create_namespaced_job(body=d, namespace='default')
    name = resp.metadata.name
    return name



  def delete( self, name ):
    resp = self.api().delete_namespaced_job(name=name, namespace='default')
    return True


  def delete_all( self ):
    resp = self.api().list_namespaced_job(namespace='default')
    for item in resp.items:
      self.delete(item.metadata.name)


  def list( self ):
    resp = self.api().list_namespaced_job(namespace='default')
    for item in resp.items:
      print(
            "%s\t%s\t%s" %
            (
             item.metadata.namespace,
             item.metadata.name,
             status_job_toString(self.status(item.metadata.name))
             ))



kube = Kubernetes()

#kube.createFromYaml( 'pi.yaml' )
#kube.createFromYaml( 'ngiax.yaml' )
#kube.status('pi94')
kube.list()
kube.delete_all()
kube.list()