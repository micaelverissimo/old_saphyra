
__all__ = [ "StatusJob", "status_job_toString" ]

from lps_cluster import EnumStringification


class StatusJob ( EnumStringification ):

  BROKEN = -3
  FAILED = -2
  KILLED = -1
  DONE = 0
  REGISTERED = 1
  ACTIVATED = 2
  STARTING = 3
  RUNNING  = 4


def status_job_toString( status ):
  if status is StatusJob.BROKEN:
    return "Broken"
  elif status is StatusJob.FAILED:
    return "Failed"
  elif status is StatusJob.KILLED:
    return "Killed"
  elif status is StatusJob.DONE:
    return "Done"
  elif status is StatusJob.REGISTERED:
    return "Registered"
  elif status is StatusJob.ACTIVATED:
    return "Activated"
  else: #status is StatusJob.RUNNING:
    return "Running"



