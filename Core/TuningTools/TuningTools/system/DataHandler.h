#ifndef TUNINGTOOLS_SYSTEM_DATAHANDLER_H
#define TUNINGTOOLS_SYSTEM_DATAHANDLER_H

#include "TuningTools/system/defines.h"

#include <vector>
#include <iostream>
#include <algorithm>    // std::copy
#include <ctime>

#include <boost/python.hpp>
#include <boost/python/stl_iterator.hpp>

#include "TuningTools/system/util.h"

/**
template<typename T> struct is_vector : public std::false_type {};

template<typename T, typename A>
struct is_vector< std::vector<T, A> > : public std::true_type {};
**/

namespace py = boost::python;

template <class Type> class DataHandler
{
  private:

    double tictac;
    vector<Type> *vec;
    /// Holds the number of rows the array has.
    unsigned numRows;
    /// Holds the number of collumns the array has.
    unsigned numCols;

  
  public:
  
    ///Default constructor
    //DataHandler( py::list data, const unsigned cols )
    //  : numRows(1),
    //    numCols(cols)
    //{
    //  tictac = 0.0;
    //  numRows = py::len(data)/numCols; 
    //  time_t tstart, tend; 
    //  tstart = time(0);
    //  vec = new std::vector<Type>(numRows*numCols);
    //  std::copy(boost::python::stl_input_iterator<Type>(data), boost::python::stl_input_iterator<Type>(), vec->begin());
    //  tend = time(0); 
    //  tictac = difftime(tend, tstart);
    //}

    DataHandler( Type *ptr, const unsigned rows, const unsigned cols )
      : numRows(rows),
        numCols(cols)
    {
      tictac = 0.0;
      vec = new vector<Type>(numRows*numCols);
      std::copy(ptr, ptr + numRows*numCols, vec->begin());
    }

    //DataHandler( std::vector<Type>& vec, const unsigned cols )
    //  : vec(&vec)
    //{
    //  numCols = vec.size();
    //  if ( is_vector< vec::value_type > ){
    //    if ( vec.size() > 0 ) {
    //      numRows = vec[0].size();
    //    } else {
    //      numRows = 0;
    //    }
    //  } else {
    //    numRows = 1;
    //  }
    //}

    ~DataHandler()
    {
      delete vec;
    }

    unsigned size(){ return vec->size(); }; 

    /// Set value to vector
    void setValue(const unsigned row, const unsigned col, Type value)
    {
      (*vec)[col + (numCols*row)] = value;
    }

    /// get value from vector
    Type getValue(const unsigned row, const unsigned col) const
    {
      return (*vec)[col + (numCols*row)];
    }

    /// Get array pointer
    Type* getPtr() { return vec->data();}

    /// Get cv array pointer
    const Type* getPtr() const {return vec->data();}

    /// Get std vector
    vector<Type>* getVecPtr() const {return vec;}

    /// copy vector to extern vector
    void copy( vector<Type> &ref ){
      ref.insert( ref.end(),vec->begin(), vec->end() );
    }


    /**
     * @brief Access the data in the array.
     *
     * This method returns the array value in the specified indexes. This is
     * necessary, since the data in the mxArray is stored in a single 1D vector,
     * so this method must apply the necessary offset calculations in order to correctly
     * access the data. This method can be also used to write data into the array.
     *
     * @param[in] row The row index.
     * @param[in] col The collumn index.
     *
     * @return the array value at the specified position.
     **/
    Type &operator()(const unsigned row, const unsigned col) const
    {
      return (*vec)[col + (numCols*row)];
    }
   
        
    /// Return the number of row of the mxArray that we are accessing.
    unsigned getNumRows() const
    {
      return numRows;
    }
    
    
    /// Return the number of collumns of the mxArray that we are accessing.
    unsigned getNumCols() const
    {
      return numCols;
    }
    
    
    ///Print the first 5 rows values into the array. using for debug.
    void showInfo() const
    {
      for(unsigned i=0; i < 5; ++i){
        for(unsigned j=0; j < numCols; ++j){
          cout << "[" << i << "][" << j << "] = " << getValue(i,j) << endl;
        }
      }
    }

    //double tictac(){return tictac;};

};

#endif
