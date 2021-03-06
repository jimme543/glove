/***********************************************************************
TranslationTransformation - Class for n-dimensional translations.
Copyright (c) 2003-2005 Oliver Kreylos

This file is part of the Templatized Geometry Library (TGL).

The Templatized Geometry Library is free software; you can redistribute
it and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of the
License, or (at your option) any later version.

The Templatized Geometry Library is distributed in the hope that it will
be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with the Templatized Geometry Library; if not, write to the Free
Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
02111-1307 USA
***********************************************************************/

#define GEOMETRY_TRANSLATIONTRANSFORMATION_IMPLEMENTATION

#ifndef METHODPREFIX
	#ifdef NONSTANDARD_TEMPLATES
		#define METHODPREFIX inline
	#else
		#define METHODPREFIX
	#endif
#endif

#include <Geometry/TranslationTransformation.h>

namespace Geometry {

/**************************************************
Static elements of class TranslationTransformation:
**************************************************/

template <class ScalarParam,int dimensionParam>
const TranslationTransformation<ScalarParam,dimensionParam> TranslationTransformation<ScalarParam,dimensionParam>::identity; // Default constructor creates identity transformation!

#if !defined(NONSTANDARD_TEMPLATES)

/***********************************************************************************
Force instantiation of all standard TranslationTransformation classes and functions:
***********************************************************************************/

template class TranslationTransformation<float,2>;
template class TranslationTransformation<double,2>;
template class TranslationTransformation<float,3>;
template class TranslationTransformation<double,3>;

#endif

}
