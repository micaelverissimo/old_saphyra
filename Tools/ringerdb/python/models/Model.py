
__all__ = ["Model"]

from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, JSON, Time
from sqlalchemy.orm import relationship
from ringerdb.models import Base


class Model( Base ):
  __tablename__ = "model"

  id            = Column( Integer, primary_key = True )
  job           = relationship( "Job", order_by='Job.id', back_populates='models')
  jobId         = Column( Integer, ForeignKey('job.id' )) 
  taskId        = Column( Integer ) 
  modelId       = Column( Integer )
  sort          = Column( Integer )
  init          = Column( Integer )
  etBinIdx      = Column( Integer )
  etaBinIdx     = Column( Integer )
  time          = Column( Time )

  # Extra column to append any other information in json format
  metadataInfo   = Column( JSON , default="{}")

  # train summary
  mse           = Column( Float )
  mse_val       = Column( Float )
  mse_op        = Column( Float )
  
  # train summary
  auc           = Column( Float )
  auc_val       = Column( Float )
  auc_op        = Column( Float )


  # set by the max sp threshold in train data
  max_sp        = Column( Float )
  max_sp_pd     = Column( Float )
  max_sp_fa     = Column( Float )
  
  # set by the max sp threshold in train data
  acc           = Column( Float )
  f1_score      = Column( Float )
  precision_score = Column( Float )
  recall_score  = Column( Float )


  # set by the max sp threshold in validation data
  max_sp_val    = Column( Float )
  max_sp_pd_val = Column( Float )
  max_sp_fa_val = Column( Float )

  # set by the max sp threshold in validation data
  acc_val           = Column( Float )
  f1_score_val      = Column( Float )
  precision_score_val = Column( Float )
  recall_score_val  = Column( Float )


  # set by the max sp threshold in validation data
  max_sp_op     = Column( Float )
  max_sp_pd_op  = Column( Float )
  max_sp_fa_op  = Column( Float )

  # set by the max sp threshold in validation data
  acc_op           = Column( Float )
  f1_score_op      = Column( Float )
  precision_score_op = Column( Float )
  recall_score_op  = Column( Float )



  

  # PileupFit variables defined in: https://github.com/jodafons/saphyra/blob/master/Core/saphyra/python/posproc/PileupFit.py
  sp_ref = Column( Float )
  pd_ref = Column( Float )
  pd_passed_ref = Column( Float )
  pd_total_ref = Column( Float )
  fa_ref = Column( Float )
  fa_passed_ref = Column( Float )
  fa_total_ref = Column( Float )
  reference = Column( String )

  slope = Column( Float )
  offset = Column( Float )

  fit_sp = Column( Float )
  fit_pd = Column( Float )
  fit_pd_total = Column( Float )
  fit_pd_passed = Column( Float )
  fit_fa = Column( Float )
  fit_fa_total = Column( Float )
  fit_fa_passed = Column( Float )
  
  fit_sp_val = Column( Float )
  fit_pd_val = Column( Float )
  fit_pd_total_val = Column( Float )
  fit_pd_passed_val = Column( Float )
  fit_fa_val = Column( Float )
  fit_fa_total_val = Column( Float )
  fit_fa_passed_val = Column( Float )

  slope_op = Column( Float )
  offset_op = Column( Float )
  
  fit_sp_op = Column( Float )
  fit_pd_op = Column( Float )
  fit_pd_total_op = Column( Float )
  fit_pd_passed_op = Column( Float )
  fit_fa_op = Column( Float )
  fit_fa_total_op = Column( Float )
  fit_fa_passed_op = Column( Float )


  def setModelId(self,id):
    self.modelId=id

  def getModelId(self):
    return self.modelId

  def setSort( self, sort ):
    self.sort = sort

  def getSort(self):
    return self.sort

  def setInit( self, init ):
    self.init = init

  def getInit( self ):
    return self.init


  def setEtBinIdx(self, idx):
    self.etBinIdx = idx

  def getEtBinIdx(self):
    return self.etBinIdx

  def setEtaBinIdx(self, idx):
    self.etaBinIdx = idx

  def getEtaBinIdx(self):
    return self.etaBinIdx


  def setSummary( self, d ):

    self.mse                      = d['mse']
    self.auc                      = d['auc']
    self.max_sp                   = d['max_sp']
    self.max_sp_pd                = d['max_sp_pd']
    self.max_sp_fa                = d['max_sp_fa']
    self.acc                      = d['acc']
    self.precision_score          = d['precision_score']
    self.recall_score             = d['recall_score']
    self.f1_score                 = d['f1_score']
    self.mse_val                  = d['mse_val']
    self.auc_val                  = d['auc_val']
    self.max_sp_val               = d['max_sp_val']
    self.max_sp_pd_val            = d['max_sp_pd_val']
    self.max_sp_fa_val            = d['max_sp_fa_val']
    self.acc_val                  = d['acc_val']
    self.precision_score_val      = d['precision_score_val']
    self.recall_score_val         = d['recall_score_val']
    self.f1_score_val             = d['f1_score_val']
    self.mse_op                   = d['mse_op']
    self.auc_op                   = d['auc_op']
    self.max_sp_op                = d['max_sp_op']
    self.max_sp_pd_op             = d['max_sp_pd_op']
    self.max_sp_fa_op             = d['max_sp_fa_op']
    self.acc_op                   = d['acc_op']
    self.precision_score_op       = d['precision_score_op']
    self.recall_score_op          = d['recall_score_op']
    self.f1_score_op              = d['f1_score_op']






  def setFitting( self , d ):

    self.sp_ref               = d['sp_ref']
    self.pd_ref               = d['pd_ref'][0]
    self.pd_passed_ref        = d['pd_ref'][1]
    self.pd_total_ref         = d['pd_ref'][2]
    self.fa_ref               = d['fa_ref'][0]
    self.fa_passed_ref        = d['fa_ref'][1]
    self.fa_total_ref         = d['fa_ref'][2]
    self.reference            = d['reference']
    self.fit_sp               = d['sp']
    self.fit_pd               = d['pd'][0]
    self.fit_pd_passed        = d['pd'][1]
    self.fit_pd_total         = d['pd'][2]
    self.fit_fa               = d['fa'][0]
    self.fit_fa_passed        = d['fa'][1]
    self.fit_fa_total         = d['fa'][2]
    self.fit_sp_val           = d['sp_val']
    self.fit_pd_val           = d['pd_val'][0]
    self.fit_pd_passed_val    = d['pd_val'][1]
    self.fit_pd_total_val     = d['pd_val'][2]
    self.fit_fa_val           = d['fa_val'][0]
    self.fit_fa_passed_val    = d['fa_val'][1]
    self.fit_fa_total_val     = d['fa_val'][2]
    self.fit_sp_op            = d['sp_op']
    self.fit_pd_pd            = d['pd_op'][0]
    self.fit_pd_passed_op     = d['pd_op'][1]
    self.fit_pd_total_op      = d['pd_op'][2]
    self.fit_fa_op            = d['fa_op'][0]
    self.fit_fa_passed_op     = d['fa_op'][1]
    self.fit_fa_total_op      = d['fa_op'][2]
    self.slope                = d['slope']
    self.offset               = d['offset']
    self.slope_op             = d['slope_op']
    self.offset_op            = d['offset_op']



  def setMetadataInfo(self, meta):
    self.metadataInfo=meta

  def getMetadataInfo(self):
    return self.metadataInfo





