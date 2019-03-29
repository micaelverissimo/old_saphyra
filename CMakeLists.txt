# Copyright (C) 2002-2017 CERN for the benefit of the ATLAS collaboration
#
# This is a template for a CMakeLists.txt file that can be used in a client
# project (work area) to set up building ATLAS packages against the configured
# release.
#

# Set the minimum required CMake version:
cmake_minimum_required( VERSION 3.2 FATAL_ERROR )

# If there's a directory called AtlasCMake in the project,
# and the user didn't specify AtlasCMake_DIR yet, then let's
# give it a default value.
if( IS_DIRECTORY ${CMAKE_SOURCE_DIR}/Build/AtlasCMake AND
      NOT AtlasCMake_DIR AND NOT ENV{AtlasCMake_DIR} )
   set( AtlasCMake_DIR ${CMAKE_SOURCE_DIR}/Build/AtlasCMake )
endif()

# If there's a directory called AtlasLCG in the project,
# and the user didn't specify LCG_DIR yet, then let's
# give it a default value.
if( IS_DIRECTORY ${CMAKE_SOURCE_DIR}/Build/AtlasLCG AND
      NOT LCG_DIR AND NOT ENV{LCG_DIR} )
   set( LCG_DIR ${CMAKE_SOURCE_DIR}/Build/AtlasLCG )
endif()

# Pick up a local version of the AtlasCMake code if it exists:
find_package( AtlasCMake QUIET )

# Find the project that we depend on:
find_package( AnalysisBase )

# Set up CTest:
atlas_ctest_setup()

# Set up a work directory project:
atlas_project( WorkDir 21.2.9
   USE AnalysisBase 21.2.9
    )

# Set up the runtime environment setup script(s):
lcg_generate_env( SH_FILE ${CMAKE_BINARY_DIR}/${ATLAS_PLATFORM}/env_setup.sh )
install( FILES ${CMAKE_BINARY_DIR}/${ATLAS_PLATFORM}/env_setup.sh
   DESTINATION . )

# Set up CPack:
atlas_cpack_setup()
