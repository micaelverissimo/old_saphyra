################################################################################
# Package: TuningTools
################################################################################

if($ENV{Athena_SETUP} STREQUAL "on")
  # Declare the package name:
  atlas_subdir( TuningTools )
  
  if( XAOD_STANDALONE )
    # We don't install TuningTools on GRID if we are on XAOD_STANDALONE mode
    if( NOT DEFINED $ENV{PanDA_TaskID} )
      # Declare the package's dependencies:
      atlas_depends_on_subdirs( PUBLIC
                                RingerCore
                                #ElectronPhotonSelectorTools
                                #RingerSelectorTools
                                PRIVATE
                                #${extra_dep}
                                )
  
      # External dependencies:
      find_package( Boost COMPONENTS python )
      #find_package( ROOT COMPONENTS Core Hist Gpad Tree MathCore Hist MathMore RIO )
      find_package( ROOT COMPONENTS Core Hist Tree RIO Hist )
      set( Python_ADDITIONAL_VERSIONS 2.7.13 2.7.5)
      find_package( PythonInterp REQUIRED)
      find_package( PythonLibs REQUIRED)
  
      ### If needed to find numpy check caffe script
      ### Also consider taking a look at: https://github.com/UCATLAS/xAODAnaHelpers/blob/master/CMakeLists.txt
  
      set (NUMPY_INCLUDE_DIR ${CMAKE_PYTHON_OUTPUT_DIRECTORY}/numpy/core/include)
      #set (CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${NUMPY_INCLUDE_DIR}")
      #set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${NUMPY_INCLUDE_DIR}")
      #ExternalProject_Get_Property(project_a install_dir)
      include_directories(${NUMPY_INCLUDE_DIR})
  
      #include(FindPackageHandleStandardArgs)
      #find_package_handle_standard_args(NumPy REQUIRED_VARS NUMPY_INCLUDE_DIR NUMPY_VERSION
      #                                        VERSION_VAR   NUMPY_VERSION)
  
      #if(NUMPY_FOUND)
      #  message(STATUS "NumPy ver. ${NUMPY_VERSION} found (include: ${NUMPY_INCLUDE_DIR})")
      #endif()
  
      #get_cmake_property(_variableNames VARIABLES)
      #foreach (_variableName ${_variableNames})
      #    message(STATUS "${_variableName}=${${_variableName}}")
      #endforeach()
  
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
      endif()
  
      # https://github.com/scipy/scipy/releases/download/v1.0.0/scipy-1.0.0.tar.gz
  
      #if( NUMPY_FOUND AND Boost_PYTHON_FOUND AND PYTHONLIBS_FOUND )
      if( Boost_PYTHON_FOUND AND PYTHONLIBS_FOUND )
        # New style root dictionary:
        atlas_add_root_dictionary( TuningToolsLib TuningToolsDictSource
                                  ROOT_HEADERS TuningTools/*.h Root/LinkDef.h
                                  EXTERNAL_PACKAGES ROOT
        )
        # Then we can proceed to a full installation:
        atlas_add_library( TuningToolsLib
                           Root/*.cxx ${TuningToolsDictSource}
                           PUBLIC_HEADERS TuningTools
                           INCLUDE_DIRS ${Boost_INCLUDE_DIRS} ${ROOT_INCLUDE_DIRS} ${PYTHON_INCLUDE_DIR} # ${PYTHON_INCLUDE_DIRS} ${NUMPY_INCLUDE_DIR}
                           LINK_LIBRARIES ${Boost_PYTHON_LIBRARIES} ${ROOT_LIBRARIES} ${PYTHON_LIBRARIES} RingerCoreLib
                         )
                       #add_dependencies(TuningToolsLib numpy)
      else()
        message( STATUS "TuningTools will be built without FastNet core!" )
      endif()
  
  
    list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/cmake")
    include(SetupPythonPackage)
    setup_python_package( six
    "https://pypi.python.org/packages/16/d8/bc6316cf98419719bd59c91742194c111b6f2e85abac88e496adefaf7afe/six-1.11.0.tar.gz"
    "d12789f9baf7e9fb2524c0c64f1773f8")
    setup_python_package( theano
    "https://github.com/Theano/Theano/archive/rel-1.0.1.tar.gz"
    "e44ea077bfeff9ae0544a1564e3a3728")
    add_dependencies(theano six )
  #setup_python_package( tensorflow
  # "https://github.com/tensorflow/tensorflow/archive/v1.4.1.tar.gz"
  # "48f80fd5ee1116f24d6f943308620a7c"
  #  SETUP "tensorflow/tensorflow/tools/pip_package/setup.py"
  #  )
    setup_python_package( keras 
    "https://github.com/keras-team/keras/archive/2.1.2.tar.gz"
    "3bbb0bafdb0da24848057722aec84795"
    ARG_DEPENDS theano )
    #ARG_DEPENDS theano tensorflow)
    #add_dependencies(keras theano tensorflow)
    add_dependencies(keras theano )
  
    endif()
  endif()
  
  # Install files from the package:
  atlas_install_python_modules( python/*.py python/dataframe python/keras_util python/monitoring python/parsers python/misc )
  atlas_install_scripts( scripts/standalone/* scripts/grid_scripts/* )


else()
  include_directories(${CMAKE_SOURCE_DIR} ${ROOT_INCLUDE_DIRS} ${CMAKE_CURRENT_SOURCE_DIR} )
  include_directories(${NUMPY_INCLUDE_DIR})
  include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../../Gaugi )
  gaugi_install_python_modules( ${CMAKE_CURRENT_SOURCE_DIR}/python TuningTools)
  gaugi_install_scripts( ${CMAKE_CURRENT_SOURCE_DIR}/scripts/grid_scripts)
  gaugi_install_scripts( ${CMAKE_CURRENT_SOURCE_DIR}/scripts/standalone)
  
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
 

 endif() 
