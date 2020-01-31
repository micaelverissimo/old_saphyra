################################################################################
# Package: TuningTools
################################################################################

#include_directories(${CMAKE_SOURCE_DIR} ${ROOT_INCLUDE_DIRS} ${CMAKE_CURRENT_SOURCE_DIR} )
#include_directories(${NUMPY_INCLUDE_DIR})
#include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../../Gaugi )
#gaugi_install_python_modules( ${CMAKE_CURRENT_SOURCE_DIR}/python TuningTools)
#gaugi_install_scripts( ${CMAKE_CURRENT_SOURCE_DIR}/scripts/grid_scripts)
#gaugi_install_scripts( ${CMAKE_CURRENT_SOURCE_DIR}/scripts/standalone)

#option(BUILD_FASTNET "Build test programs" ON)
#
#
#
#if (NOT DEFINED _USING_MULT_THREAD)
#    set(_USING_MULT_THREAD 1)
#endif()
#if (NOT DEFINED TUNINGTOOL_DBG_LEVEL)
#    set(TUNINGTOOL_DBG_LEVEL 0)
#endif()
#message( STATUS "TuningTools cxx debug log verbosity is set to: ${TUNINGTOOL_DBG_LEVEL}" )
#add_definitions(-DUSING_MULTI_THREAD=${_USING_MULT_THREAD}
#  -D__TUNINGTOOLS_LIBRARY_NAME__=libsaphyra
#                -DTUNINGTOOL_DBG_LEVEL=${TUNINGTOOL_DBG_LEVEL}
#                )
#
##if( NUMPY_FOUND AND Boost_PYTHON_FOUND AND PYTHONLIBS_FOUND )
#if( Boost_PYTHON_FOUND AND PYTHONLIBS_FOUND )
#  file(GLOB_RECURSE HEADERS TuningTools/*)
#  file(GLOB_RECURSE SOURCES Root/*.cxx)
#  message( STATUS ${HEADERS}) 
#  message( STATUS ${SOURCES}) 
#  ROOT_GENERATE_DICTIONARY(TuningToolsDict  ${HEADERS}
#                                            LINKDEF
#                                            Root/LinkDef.h
#                                            MODULE
#                                            TuningTools
#                                            DEPENDENCIES
#                                            Gaugi)
#  #Create the CustomClasses library with the ROOT dictionary.
#  add_library(TuningTools OBJECT  ${SOURCES} TuningToolsDict.cxx)
#  #Link to ROOT.
#  install(FILES ${HEADERS}  DESTINATION TuningTools)






#else()
#  message( STATUS "TuningTools will not have FastNet core available!" )
#endif()


