find_package(ROOT)

if ( ${ROOT_FOUND} )
  if(DEFINED ENV{WCSIMDIR})
    include_directories($ENV{WCSIMDIR}/include)
    include_directories(${ROOT_INCLUDE_DIRS})

    list(APPEND CMAKE_MODULE_PATH "$ENV{ROOTSYS}/cmake/modules")

    #include(RootNewMacros)
    GET_FILENAME_COMPONENT(ROOT_CMAKE_DIR "${ROOT_USE_FILE}" DIRECTORY)
    FIND_FILE(ROOT_MACROS_FILE
	      #NAMES RootNewMacros.cmake	  
	      NAMES RootNewMacros
              HINTS ${ROOT_CMAKE_DIR}/modules/ $ENV{ROOTSYS}/../cmake/modules $ENV{ROOTSYS}/cmake/modules)  
    IF(NOT ROOT_MACROS_FILE)
    	   MESSAGE(WARNING "Cannot find ROOT macros, including generic file as fallback.")	
	   INCLUDE("${ROOT_USE_FILE}")
    ELSE()
	INCLUDE(${ROOT_MACROS_FILE})
	ENDIF()

    ROOT_GENERATE_DICTIONARY(WCSimRootDict $ENV{WCSIMDIR}/include/WCSimRootEvent.hh $ENV{WCSIMDIR}/include/WCSimRootGeom.hh $ENV{WCSIMDIR}/include/WCSimPmtInfo.hh $ENV{WCSIMDIR}/include/WCSimEnumerations.hh  $ENV{WCSIMDIR}/include/WCSimRootOptions.hh $ENV{WCSIMDIR}/include/WCSimRootTools.hh LINKDEF $ENV{WCSIMDIR}/include/WCSimRootLinkDef.hh)

    add_library(WCSimRoot SHARED $ENV{WCSIMDIR}/src/WCSimRootEvent.cc $ENV{WCSIMDIR}/src/WCSimRootGeom.cc $ENV{WCSIMDIR}/src/WCSimPmtInfo.cc $ENV{WCSIMDIR}/src/WCSimEnumerations.cc $ENV{WCSIMDIR}/src/WCSimRootOptions.cc $ENV{WCSIMDIR}/src/WCSimRootTools.cc WCSimRootDict.cxx)
    target_link_libraries(WCSimRoot  ${ROOT_LIBRARIES})
    
    pybind11_add_module(py_wcsim_reader SHARED py_wcsim_reader.cc $ENV{WCSIMDIR}/src/WCSimRootEvent.cc $ENV{WCSIMDIR}/src/WCSimRootGeom.cc)
    target_link_libraries(py_wcsim_reader PRIVATE ${ROOT_LIBRARIES} WCSimRoot)	
  endif()
endif()


