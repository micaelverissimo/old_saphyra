################################################################################
# Package: prometheus
################################################################################

if($ENV{Athena_SETUP} STREQUAL "on")
  # Declare the package name:
  atlas_subdir( tableboard )
  # Install files from the package:
  atlas_install_python_modules( python/*.py )
else()

  gaugi_install_python_modules( ${CMAKE_CURRENT_SOURCE_DIR}/python tableboard)
endif()

