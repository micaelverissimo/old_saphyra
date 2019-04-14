#include "TuningTools/MuonPhysVal.h"
#include "TuningTools/RingerPhysVal.h"
#include "TuningTools/RingerPhysVal_v2.h"
#include "TuningTools/SkimmedNtuple.h"
#include "TuningTools/SkimmedNtuple_v2.h"
//#include <vector>

#if defined(__CLING__) || defined(__CINT__)
#pragma link off all globals;
#pragma link off all classes;
#pragma link off all functions;
#pragma link C++ nestedclass;

// Create dictionaries for the used vector types:
//#pragma link C++ class std::vector<float>+;
//#pragma link C++ class std::vector< std::vector<float> >+;
//#pragma link C++ class std::vector<int8_t>+;

// And for the event model class:
#pragma link C++ class RingerPhysVal+;
#pragma link C++ class RingerPhysVal_v2+;
#pragma link C++ class MuonPhysVal+;
#pragma link C++ class SkimmedNtuple+;
#pragma link C++ class SkimmedNtuple_v2+;

#endif
