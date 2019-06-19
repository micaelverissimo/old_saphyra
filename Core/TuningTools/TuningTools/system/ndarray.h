#ifndef NDARRAY_H
#define NDARRAY_H

#include <boost/python.hpp>
namespace py = boost::python;

#include "TuningTools/system/defines.h"

/** 
 * @brief C++ interface for easy access to numpy arrays 
 *
 * Source: 
 * http://wiki.scipy.org/Wiki/C%2B%2B_Extensions_that_use_NumPy_arrays?action=AttachFile&do=get&target=ndarray.h
 *
 * In fact, we shall stop using this class and use the DataHandle instead but,
 * for now, we keep this.
 *
 * @author J. De Ridder
 * @author W. S. Freund (all modifications w.r.t source)
 **/

/// Traits need to used because the return type of the []-operator can be
/// a subarray or an element, depending whether all the axes are exhausted.
template<typename datatype, int ndim> class Ndarray;

/**
 * @brief Primary template for returning reduced Ndarray dimensional array
 **/
template<typename datatype, int ndim>
struct getItemTraits
{
  typedef Ndarray<datatype, ndim-1> returnType;
  typedef const Ndarray<datatype, ndim-1> constReturnType;
};

/**
 * @brief Specialization for unidimentional return type:
 **/
template<typename datatype>
struct getItemTraits<datatype, 1>
{
  typedef datatype& returnType;
  typedef const datatype& constReturnType;
};


/**
 * @brief Better representation for the numpy array on C++
 *
 *  The class holds a pointer to the numpy data, its shape and 
 * the strides for pointer in each dimension.
 *  It does not own the elements, but is rather a wrapper for 
 * reading the elements on C++.
 **/
template<typename datatype, int ndim>
class Ndarray
{

  private:

    /// @brief numpy data raw pointer
    datatype *m_data;
    /// @brief numpy shape raw pointer
    npy_intp *m_shape;
    /// @brief numpy raw pointer strides for each dimensional
    npy_intp m_steps[ndim];

    // @brief hold the smart pointer to enlarge numpy life span
    py::handle<PyObject> m_handle;

  public:

    /// Typedef for the holden data type
    typedef datatype data_t;

    /// Typedef for the holden pointer type
    typedef datatype* pointer_t;

    /// Typedef for the holden pointer type
    typedef const datatype* const_pointer_t;


    /// Ctors
    /// @{
    /// Empty ctor:
    Ndarray(){;}
    /// Ndarray constructor
    Ndarray(datatype * const data, 
            npy_intp * const shape, 
            const npy_intp * const steps);
    /// Ndarray copy constructor
    Ndarray(const Ndarray<datatype, ndim>& array);
    /// Ndarray constructor from ctypes structure
    //Ndarray(const numpyArray<datatype>& array);
    /// ctor from python arrays
    Ndarray(const py::handle<PyObject> &handle);
    /// @}

    /// Ndarray method to get length of given axis
    npy_intp getShape(const int axis) const;

    /**
     * @brief Ndarray overloaded []-operator.
     *
     * The [i][j][k] selection is recursively replaced by
     * i*steps[0]+j*steps[1]+k*steps[2] at compile time, using template
     * meta-programming. If the axes are not exhausted, return a subarray, else
     * return an element.
     **/
    typename getItemTraits<datatype, ndim>::returnType operator[](npy_intp i);

    /**
     * @brief const version of []-operator
     **/
    typename getItemTraits<datatype, ndim>::constReturnType operator[](npy_intp i) const;

    /// @brief Retrieves raw data pointer
    pointer_t getPtr();

    /// @brief Retrieves cv raw data pointer
    const_pointer_t getPtr() const;

    /// @brief Returns whether the Ndarray is empty
    bool empty() const;
};


//==============================================================================
template<typename datatype, int ndim>
Ndarray<datatype, ndim>::Ndarray(datatype *const data, 
                                 npy_intp *const shape, 
                                 const npy_intp *const steps)
  : m_data(nullptr)
{
  this->m_data = data;
  this->m_shape = shape;
  for ( int i = 0; i < ndim; ++i){
    this->m_steps[i] = steps[i];
  }
}


//==============================================================================
template<typename datatype, int ndim>
Ndarray<datatype, ndim>::Ndarray(const Ndarray<datatype, ndim>& array)
  : m_data(nullptr),
    m_shape(nullptr)
{
  // FIXME Shouldn't this copy data?
  this->m_data = array.m_data;
  this->m_shape = array.m_shape;
  for ( int i = 0; i < ndim; ++i){
    this->m_steps[i] = array.m_steps[i];
  }
}

//==============================================================================
template<typename datatype, int ndim>
Ndarray<datatype, ndim>::Ndarray(const py::handle<PyObject> &handle)
  : m_data(nullptr)
{
  this->m_data    = reinterpret_cast<datatype*>(PyArray_DATA(handle.get()));
  this->m_shape   = PyArray_DIMS( handle.get() );
  int itemsize = PyArray_ITEMSIZE( handle.get() );
  for ( int i = 0; i < ndim; ++i){
    this->m_steps[i] = PyArray_STRIDE( handle.get(), i )/ itemsize;
  }
  this->m_handle  = handle;
}

//==============================================================================
template<typename datatype, int ndim>
npy_intp Ndarray<datatype, ndim>::getShape(const int axis) const
{
  if ( m_shape && axis < ndim && axis >= 0) {
    return this->m_shape[axis];
  } else {
    return 0;
  }
}

//==============================================================================
template<typename datatype, int ndim>
  typename getItemTraits<datatype, ndim>::returnType
Ndarray<datatype, ndim>::operator[](npy_intp i)
{
  if ( m_data ) {
    return Ndarray<datatype, ndim-1>( &this->m_data[i*this->m_steps[0]], 
        &this->m_shape[1], 
        &this->m_steps[1]);
  } else {
    throw std::runtime_error("Attempted to access ndarray with no data!");
  }
}

//==============================================================================
template<typename datatype, int ndim>
  typename getItemTraits<datatype, ndim>::constReturnType
Ndarray<datatype, ndim>::operator[](npy_intp i) const
{
  if ( m_data ) {
    return Ndarray<datatype, ndim-1>( &this->m_data[i*this->m_steps[0]], 
        &this->m_shape[1], 
        &this->m_steps[1]);
  } else {
    throw std::runtime_error("Attempted to access ndarray with no data!");
  }
}

//==============================================================================
template<typename datatype, int ndim>
  typename Ndarray<datatype, ndim>::pointer_t
Ndarray<datatype, ndim>::getPtr()
{
  return this->m_data;
}

//==============================================================================
template<typename datatype, int ndim>
typename Ndarray<datatype, ndim>::const_pointer_t
  Ndarray<datatype, ndim>::getPtr() const
{
  return this->m_data;
}

//==============================================================================
template<typename datatype, int ndim>
bool Ndarray<datatype, ndim>::empty() const
{
  if ( m_data == nullptr ){
    return true;
  }
  for ( int dim = 0; dim < ndim; ++dim) {
    if ( !getShape( dim ) ){
      return true;
    }
  }
  return false;
}

//==============================================================================

/**
 * @brief Template partial specialisation of Ndarray.
 *
 * For 1D Ndarrays, the [] operator should return an element, not a subarray,
 * so it needs to be special-cased. In principle only the operator[] method
 * should be specialised, but for some reason my gcc version seems to require
 * that then the entire class with all its methods are specialised.
 **/
template<typename datatype>
class Ndarray<datatype, 1>
{
  private:
    /// @brief numpy data raw pointer
    datatype *m_data;
    /// @brief numpy shape raw pointer
    npy_intp m_shape;
    /// @brief numpy raw pointer strides for each dimensional
    npy_intp m_step;

    // @brief hold the smart pointer to enlarge numpy life span
    py::handle<PyObject> m_handle;

  public:

    /// Typedef for the holden data type
    typedef datatype data_t;

    /// Typedef for the holden pointer type
    typedef datatype* pointer_t;

    /// Typedef for the holden pointer type
    typedef const datatype* const_pointer_t;

    /// Empty ctor
    Ndarray();
    /// Ndarray partial specialised constructor
    Ndarray(datatype *const data, npy_intp *const shape, const npy_intp *const step);
    /// Ndarray partially specialised copy constructor
    Ndarray(const Ndarray<datatype, 1>& array);
    /// Ndarray partially specialised constructor from ctypes structure
    //Ndarray(const numpyArray<datatype>& array);
    /// ctor from python arrays
    Ndarray(const py::handle<PyObject> &handle);

    /// Ndarray method to get length of given axis
    npy_intp getShape(const int axis = 0) const;

    /**
     * Partial specialised [] operator: for 1D arrays, return an element rather
     * than a subarray 
     **/
    typename getItemTraits<datatype, 1>::returnType operator[](npy_intp i);       

    /**
     * @brief speialised const version of []-operator
     **/
    typename getItemTraits<datatype, 1>::constReturnType operator[](npy_intp i) const;

    /// @brief Retrieves raw data pointer
    pointer_t getPtr();

    /// @brief Retrieves cv raw data pointer
    const_pointer_t getPtr() const;

    /// @brief Returns whether the Ndarray is empty
    bool empty() const;
};

//==============================================================================
template<typename datatype>
Ndarray<datatype, 1>::Ndarray()
  : m_data(nullptr){;}


//==============================================================================
template<typename datatype>
Ndarray<datatype, 1>::Ndarray(datatype *const data, 
                              npy_intp *const shape, 
                              const npy_intp *const step)
  : m_data(nullptr)
{
  this->m_data = data;
  this->m_shape = *shape;
  this->m_step = *step;
}

//==============================================================================
template<typename datatype>
Ndarray<datatype, 1>::Ndarray(const Ndarray<datatype, 1>& array)
  : m_data(nullptr)
{
  this->m_data = array.m_data;
  this->m_shape = array.m_shape;
  this->m_step = array.m_step;
}

//==============================================================================
template<typename datatype>
Ndarray<datatype, 1>::Ndarray(const py::handle<PyObject> &handle)
  : m_data(nullptr)
{
  this->m_data    = reinterpret_cast<datatype*>(PyArray_DATA(handle.get()));
  this->m_shape   = PyArray_DIM( handle.get(), 0 );
  this->m_step    = PyArray_STRIDE( handle.get(), 0) /
                                    PyArray_ITEMSIZE( handle.get() );
  this->m_handle  = handle;
}

//==============================================================================
template<typename datatype>
npy_intp Ndarray<datatype, 1>::getShape(const int axis) const
{
  if ( m_shape && axis < 1 && axis >= 0) {
    return this->m_shape;
  } else {
    return 0;
  }
}

//==============================================================================
template<typename datatype>
typename getItemTraits<datatype, 1>::returnType
Ndarray<datatype, 1>::operator[](npy_intp i)
{
  if ( m_data ) {
    return this->m_data[i*this->m_step];
  } else {
    throw std::runtime_error("Attempted to access ndarray with no data!");
  }
}

//==============================================================================
template<typename datatype>
typename getItemTraits<datatype, 1>::constReturnType 
Ndarray<datatype, 1>::operator[](npy_intp i) const
{
  if ( m_data ) {
    return this->m_data[i*this->m_step];
  } else {
    throw std::runtime_error("Attempted to access ndarray with no data!");
  }
}

//==============================================================================
template<typename datatype>
  typename Ndarray<datatype, 1>::pointer_t
Ndarray<datatype, 1>::getPtr()
{
  return this->m_data;
}

//==============================================================================
template<typename datatype>
typename Ndarray<datatype, 1>::const_pointer_t
  Ndarray<datatype, 1>::getPtr() const
{
  return this->m_data;
}

//==============================================================================
template<typename datatype>
bool Ndarray<datatype, 1>::empty() const
{
  if ( m_data && !getShape( 0 ) ){
    return true;
  }
  return false;
}

#endif // NDARRAY_H
