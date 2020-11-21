#include <vector>
#include <string>

#include <pybind11/numpy.h>
#include <pybind11/stl.h>

#include "WCSimRootEvent.hh"
#include "WCSimRootGeom.hh"

#include "TChain.h"

namespace py = pybind11;

struct pmt;
struct trueTrack;
struct hit;

class py_wcsim_reader {

  TChain * eventChain;
  TChain * geometryChain;

  WCSimRootEvent * event;
  WCSimRootGeom * geo;

  bool geometryInitialized;
  
 public :
  py_wcsim_reader();

  void addFile(std::string fileName);

  uint32_t N_events;
  
  uint32_t N_PMTs;

  float cylinder_radius;
  float cylinder_half_height;

  py::array_t<pmt> pmtInfo;

  int loadEvent(int i);
  py::array_t<hit> getHits(int trigger);
  py::array_t<trueTrack> getTrueTracks(int trigger);
  
};
