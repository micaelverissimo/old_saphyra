#ifndef TUNINGTOOLS_SYSTEM_MACROS_H
#define TUNINGTOOLS_SYSTEM_MACROS_H

#include "TuningTools/system/defines.h"

/**
 * @brief Redirect from this class a getter and setter to a pointer member
 *        property
 **/
#define MEMBER_POINTER_OBJECT_SETTER_AND_GETTER(OBJ, TYPE, SETTER, GETTER)     \
                                                                               \
  const TYPE& GETTER() const {                                                 \
    return this->OBJ->GETTER();                                                \
  }                                                                            \
                                                                               \
  void SETTER(const TYPE& value){                                              \
    this->OBJ->SETTER(value);                                                  \
  }

/**
 * @brief Redirect from this class a getter and setter to a pointer member
 *        property
 **/
#define MEMBER_POINTER_PRIMITIVE_SETTER_AND_GETTER(OBJ, TYPE, SETTER, GETTER)  \
                                                                               \
  TYPE GETTER() const {                                                        \
    return this->OBJ->GETTER();                                                \
  }                                                                            \
                                                                               \
  void SETTER(const TYPE value){                                               \
    this->OBJ->SETTER(value);                                                  \
  }

/**
 * @brief Redirect from this class a getter and setter to a member property
 **/
#define MEMBER_OBJECT_SETTER_AND_GETTER(OBJ, TYPE, SETTER, GETTER)             \
                                                                               \
  const TYPE& GETTER() const {                                                 \
    return this->OBJ.GETTER();                                                 \
  }                                                                            \
                                                                               \
  void SETTER(const TYPE& value){                                              \
    this->OBJ.SETTER(value);                                                   \
  }

/**
 * @brief Redirect from this class a getter and setter to a member property
 **/
#define MEMBER_PRIMITIVE_SETTER_AND_GETTER(OBJ, TYPE, SETTER, GETTER)          \
                                                                               \
  TYPE GETTER() const {                                                        \
    return this->OBJ.GETTER();                                                 \
  }                                                                            \
                                                                               \
  void SETTER(const TYPE value){                                               \
    this->OBJ.SETTER(value);                                                   \
  }

/**
 * @brief Getter and setter for non-primitive types, where a reference should
 *        be used.
 **/
#define OBJECT_SETTER_AND_GETTER(TYPE, SETTER, GETTER, VAR)                    \
                                                                               \
  const TYPE& GETTER() const {                                                 \
    return this->VAR;                                                          \
  }                                                                            \
                                                                               \
  void SETTER(const TYPE &value){                                              \
     this->VAR = value;                                                        \
  }
 

/**
 * @brief Define getter and setter for primitive types
 **/
#define PRIMITIVE_SETTER_AND_GETTER(TYPE, SETTER, GETTER, VAR)                 \
                                                                               \
  TYPE GETTER() const {                                                        \
    return this->VAR;                                                          \
  }                                                                            \
                                                                               \
  void SETTER(const TYPE value){                                               \
    this->VAR = value;                                                         \
  }

/**
 * @brief Define setter for primitive types
 **/
#define PRIMITIVE_SETTER(TYPE, SETTER,  VAR)                                   \
                                                                               \
  void SETTER(TYPE value){                                                     \
    VAR = value;                                                               \
  }



#endif
