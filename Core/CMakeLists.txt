################################################################################
# Package: TuningTools
################################################################################

include_directories(${CMAKE_SOURCE_DIR} ${ROOT_INCLUDE_DIRS} ${CMAKE_CURRENT_SOURCE_DIR} )
include_directories(${NUMPY_INCLUDE_DIR})
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../Gaugi )


option(BUILD_FASTNET "Build test programs" ON)



if (NOT DEFINED _USING_MULT_THREAD)
    set(_USING_MULT_THREAD 1)
endif()
if (NOT DEFINED TUNINGTOOL_DBG_LEVEL)
    set(TUNINGTOOL_DBG_LEVEL 0)
endif()
message( STATUS "TuningTools cxx debug log verbosity is set to: ${TUNINGTOOL_DBG_LEVEL}" )
add_definitions(-DUSING_MULTI_THREAD=${_USING_MULT_THREAD}
                -D__TUNINGTOOLS_LIBRARY_NAME__=libTuningToolsLib
                -DTUNINGTOOL_DBG_LEVEL=${TUNINGTOOL_DBG_LEVEL}
                )

# Component(s) in the package:
find_package(OpenMP)
if (OPENMP_FOUND)
    set (CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
    set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
    set (CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${OpenMP_EXE_LINKER_FLAGS}")
endif()

# https://github.com/scipy/scipy/releases/download/v1.0.0/scipy-1.0.0.tar.gz


#if( NUMPY_FOUND AND Boost_PYTHON_FOUND AND PYTHONLIBS_FOUND )
if( Boost_PYTHON_FOUND AND PYTHONLIBS_FOUND )
  file(GLOB_RECURSE HEADERS TuningTools/*)
  file(GLOB_RECURSE SOURCES src/*.cxx)
  
  ROOT_GENERATE_DICTIONARY(TuningToolsDict  ${HEADERS}
                                            LINKDEF
                                            src/LinkDef.h
                                            MODULE
                                            TuningTools
                                            DEPENDENCIES
                                            Gaugi)
  #Create the CustomClasses library with the ROOT dictionary.
  add_library(TuningTools OBJECT  ${SOURCES} TuningToolsDict.cxx)
  #Link to ROOT.
  install(FILES ${HEADERS}  DESTINATION TuningTools)

else()
  message( STATUS "TuningTools will not have FastNet core available!" )
endif()


