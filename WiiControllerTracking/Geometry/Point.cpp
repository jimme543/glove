/***********************************************************************
Point - Class for affine points.
Copyright (c) 2001-2005 Oliver Kreylos

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

#define GEOMETRY_POINT_IMPLEMENTATION

#ifndef METHODPREFIX
	#ifdef NONSTANDARD_TEMPLATES
		#define METHODPREFIX inline
	#else
		#define METHODPREFIX
	#endif
#endif

#include <Geometry/Point.h>

namespace Geometry {

/******************************
Static elements of class Point:
******************************/

template <class ScalarParam,int dimensionParam>
const Point<ScalarParam,dimensionParam> Point<ScalarParam,dimensionParam>::origin(ScalarParam(0));

#if !defined(NONSTANDARD_TEMPLATES)

/***************************************************************
Force instantiation of all standard Point classes and functions:
***************************************************************/

template const Point<int,2> Point<int,2>::origin;

template const Point<int,3> Point<int,3>::origin;

template const Point<float,2> Point<float,2>::origin;

template const Point<float,3> Point<float,3>::origin;

template const Point<double,2> Point<double,2>::origin;

template const Point<double,3> Point<double,3>::origin;

#endif

}
