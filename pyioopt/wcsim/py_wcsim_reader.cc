#include "py_wcsim_reader.hh"

#include <vector>
#include <string>

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

#include "WCSimRootEvent.hh"
#include "WCSimRootGeom.hh"

#include "TChain.h"

struct pmt {
  float x;
  float y;
  float z;
  float dirx;
  float diry;
  float dirz;
  int32_t location;
  uint16_t row;
  uint16_t column;
};

struct trueTrack {
  int32_t PDG_code;
  int32_t flag;
  float m;
  float p;
  float E;
  int32_t startVol;
  int32_t stopVol;
  float dirx;
  float diry;
  float dirz;
  float stopx;
  float stopy;
  float stopz;
  float startx;
  float starty;
  float startz;
  int32_t parenttype;
  float time;
  int32_t id;
};

struct hit {
  uint32_t pmtNumber;
  float q;
  float t;
};

struct vertex {
  float vtx_x;
  float vtx_y;
  float vtx_z;
};

py_wcsim_reader::py_wcsim_reader(){
  
  eventChain = new TChain("wcsimT");
  geometryChain = new TChain("wcsimGeoT");

  event = new WCSimRootEvent();
  event->Initialize();
  geo = new WCSimRootGeom();

  eventChain->SetBranchAddress("wcsimrootevent", &event);
  geometryChain->SetBranchAddress("wcsimrootgeom", &geo);
  
  N_events = 0;

  //  pmtInfo = 0;
  geometryInitialized = false;
  N_PMTs = 0;

  cylinder_radius = 0.;
  cylinder_half_height = 0.;
}

void py_wcsim_reader::addFile(std::string fileName){

  eventChain->Add(fileName.c_str());
  
  N_events = eventChain->GetEntries();

  if (!geometryInitialized){
    geometryInitialized = true;
    
    geometryChain->Add(fileName.c_str());
    geometryChain->GetEntry(0);
    
    N_PMTs = geo->GetWCNumPMT();

    cylinder_radius = geo->GetWCCylRadius();
    cylinder_half_height = geo->GetWCCylLength();

    pmtInfo = py::array_t<pmt>(N_PMTs);
    py::buffer_info pmtInfo_buffer = pmtInfo.request();
    pmt * pmtInfo_pointer = static_cast<pmt *>(pmtInfo_buffer.ptr);
    
    for (uint32_t iPMT = 0; iPMT < N_PMTs; iPMT++){
      const WCSimRootPMT * thisPMT = geo->GetPMTPtr(iPMT);
      
      pmtInfo_pointer[iPMT].x = thisPMT->GetPosition(0);
      pmtInfo_pointer[iPMT].y =	thisPMT->GetPosition(1);
      pmtInfo_pointer[iPMT].z = thisPMT->GetPosition(2);
      pmtInfo_pointer[iPMT].dirx = thisPMT->GetOrientation(0);
      pmtInfo_pointer[iPMT].diry = thisPMT->GetOrientation(0);
      pmtInfo_pointer[iPMT].dirz = thisPMT->GetOrientation(0);
      pmtInfo_pointer[iPMT].location = thisPMT->GetCylLoc();
      pmtInfo_pointer[iPMT].row = 0; // To be filled on python side
      pmtInfo_pointer[iPMT].column = 0; // To be filled on python side
    }
  }
}

int py_wcsim_reader::loadEvent(int i){

  // TBranch autodelete crashes pybind11... do this manually
  delete event;
  event = new WCSimRootEvent();
  eventChain->SetBranchAddress("wcsimrootevent", &event);
  
  eventChain->GetEntry(i);
  return event->GetNumberOfEvents();
}

py::array_t<hit> py_wcsim_reader::getHits(int trigger) {

  WCSimRootTrigger * trig = event->GetTrigger(trigger);
 
  float tOffset = 0.0;
  int aTime = 0;
  int aTimeZero = 0;
  aTime = trig->GetHeader()->GetDate();
  tOffset = float(aTime - aTimeZero);

  uint32_t N_hits = trig->GetNcherenkovdigihits();

  py::array_t<hit> hits = py::array_t<hit>(N_hits);
  py::buffer_info hits_buffer = hits.request();
  hit * hits_pointer = static_cast<hit *>(hits_buffer.ptr);

  TClonesArray * wcsimHits = trig->GetCherenkovDigiHits();
  for(uint32_t iHit = 0; iHit < N_hits; iHit++){
    hits_pointer[iHit].pmtNumber = static_cast<WCSimRootCherenkovDigiHit*>(wcsimHits->operator[](iHit))->GetTubeId();
    hits_pointer[iHit].q = static_cast<WCSimRootCherenkovDigiHit*>(wcsimHits->operator[](iHit))->GetQ();
    hits_pointer[iHit].t = static_cast<WCSimRootCherenkovDigiHit*>(wcsimHits->operator[](iHit))->GetT() - tOffset;
  }
  return hits;
}

py::array_t<vertex> py_wcsim_reader::getVertex(int trigger) {

  WCSimRootTrigger * trig = event->GetTrigger(trigger);
  py::array_t<vertex> thisVertex = py::array_t<vertex>(1);
  py::buffer_info vertex_buffer = thisVertex.request();
  vertex * vertex_pointer = static_cast<vertex *>(vertex_buffer.ptr);
  vertex_pointer[0].vtx_x = trig->GetVtx(0);
  vertex_pointer[0].vtx_y = trig->GetVtx(1);
  vertex_pointer[0].vtx_z = trig->GetVtx(2);
  
  return thisVertex; 
}
 
py::array_t<trueTrack> py_wcsim_reader::getTrueTracks(int trigger){
  WCSimRootTrigger * trig = event->GetTrigger(trigger);

  uint32_t N_true_tracks = trig->GetNtrack();

  py::array_t<trueTrack> trueTracks = py::array_t<trueTrack>(N_true_tracks);
  py::buffer_info trueTracks_buffer = trueTracks.request();
  trueTrack * trueTracks_pointer = static_cast<trueTrack *>(trueTracks_buffer.ptr);
  
  TClonesArray * wcsimTracks = trig->GetTracks();

  for (uint32_t iTrack = 0; iTrack < N_true_tracks; iTrack++){
    trueTracks_pointer[iTrack].PDG_code = static_cast<WCSimRootTrack*>(wcsimTracks->operator[](iTrack))->GetIpnu();
    trueTracks_pointer[iTrack].flag = static_cast<WCSimRootTrack*>(wcsimTracks->operator[](iTrack))->GetFlag();
    trueTracks_pointer[iTrack].m = static_cast<WCSimRootTrack*>(wcsimTracks->operator[](iTrack))->GetM();
    trueTracks_pointer[iTrack].p = static_cast<WCSimRootTrack*>(wcsimTracks->operator[](iTrack))->GetP();
    trueTracks_pointer[iTrack].E = static_cast<WCSimRootTrack*>(wcsimTracks->operator[](iTrack))->GetE();
    trueTracks_pointer[iTrack].startVol = static_cast<WCSimRootTrack*>(wcsimTracks->operator[](iTrack))->GetStartvol();
    trueTracks_pointer[iTrack].stopVol = static_cast<WCSimRootTrack*>(wcsimTracks->operator[](iTrack))->GetStopvol();
    trueTracks_pointer[iTrack].dirx = static_cast<WCSimRootTrack*>(wcsimTracks->operator[](iTrack))->GetDir(0);
    trueTracks_pointer[iTrack].diry = static_cast<WCSimRootTrack*>(wcsimTracks->operator[](iTrack))->GetDir(1);
    trueTracks_pointer[iTrack].dirz = static_cast<WCSimRootTrack*>(wcsimTracks->operator[](iTrack))->GetDir(2);
    trueTracks_pointer[iTrack].stopx = static_cast<WCSimRootTrack*>(wcsimTracks->operator[](iTrack))->GetStop(0);
    trueTracks_pointer[iTrack].stopy = static_cast<WCSimRootTrack*>(wcsimTracks->operator[](iTrack))->GetStop(1);
    trueTracks_pointer[iTrack].stopz = static_cast<WCSimRootTrack*>(wcsimTracks->operator[](iTrack))->GetStop(2);
    trueTracks_pointer[iTrack].startx = static_cast<WCSimRootTrack*>(wcsimTracks->operator[](iTrack))->GetStart(0);
    trueTracks_pointer[iTrack].starty = static_cast<WCSimRootTrack*>(wcsimTracks->operator[](iTrack))->GetStart(1);
    trueTracks_pointer[iTrack].startz = static_cast<WCSimRootTrack*>(wcsimTracks->operator[](iTrack))->GetStart(2);
    trueTracks_pointer[iTrack].parenttype = static_cast<WCSimRootTrack*>(wcsimTracks->operator[](iTrack))->GetParenttype();
    trueTracks_pointer[iTrack].time = static_cast<WCSimRootTrack*>(wcsimTracks->operator[](iTrack))->GetTime();
    trueTracks_pointer[iTrack].id = static_cast<WCSimRootTrack*>(wcsimTracks->operator[](iTrack))->GetId();
  }
  return trueTracks;
}

void py_wcsim_reader::clearEvent(){
  std::cout << "CLEARING EVENT!" << std::endl;
  event->Clear();
}

PYBIND11_MODULE(py_wcsim_reader, m) {
  m.doc() = "Python module to expose c++ WCSim ROOT file reader";

  PYBIND11_NUMPY_DTYPE(pmt, x, y, z, dirx, diry, dirz, location, row, column);
  PYBIND11_NUMPY_DTYPE(trueTrack, PDG_code, flag, m, p, E, startVol, stopVol, dirx, diry, dirz,
  		 stopx, stopy, stopz, startx, starty, startz, parenttype, time, id);
  PYBIND11_NUMPY_DTYPE(hit, pmtNumber, q, t);
  PYBIND11_NUMPY_DTYPE(vertex, vtx_x, vtx_y, vtx_z);
		 
  py::class_<py_wcsim_reader>(m, "py_wcsim_reader")
    .def(py::init())
    .def("addFile", &py_wcsim_reader::addFile)
    .def_readonly("N_events", &py_wcsim_reader::N_events)
    .def_readonly("N_PMTs", &py_wcsim_reader::N_PMTs)
    .def_readonly("cylinder_radius", &py_wcsim_reader::cylinder_radius)
    .def_readonly("cylinder_half_height", &py_wcsim_reader::cylinder_half_height)
    .def_readwrite("pmtInfo", &py_wcsim_reader::pmtInfo)
    .def("loadEvent", &py_wcsim_reader::loadEvent)
    .def("getHits", &py_wcsim_reader::getHits)
    .def("getTrueTracks", &py_wcsim_reader::getTrueTracks)
    .def("getVertex", &py_wcsim_reader::getVertex)
    .def("clearEvent", &py_wcsim_reader::clearEvent);
};


