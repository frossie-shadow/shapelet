#!/usr/bin/env python

#
# LSST Data Management System
# Copyright 2008-2014 LSST Corporation.
#
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the LSST License Statement and
# the GNU General Public License along with this program.  If not,
# see <http://www.lsstcorp.org/LegalNotices/>.
#

import unittest
import numpy

import lsst.utils.tests
import lsst.afw.geom.ellipses
import lsst.shapelet.tests
import lsst.afw.image

numpy.random.seed(500)

class MatrixBuilderTestCase(lsst.shapelet.tests.ShapeletTestCase):

    def setUp(self):
        self.xD = numpy.random.randn(50)
        self.yD = numpy.random.randn(50)
        self.xF = self.xD.astype(numpy.float32)
        self.yF = self.yD.astype(numpy.float32)

    def checkAccessors(self, obj, basisSize):
        self.assertEqual(obj.getDataSize(), self.xD.size)
        self.assertEqual(obj.getBasisSize(), basisSize)

    def testSimpleShapeletMatrixBuilder(self):
        function = self.makeRandomShapeletFunction(order=4)
        size = function.getCoefficients().size
        function.getCoefficients()[:] = numpy.random.randn(size)
        basis = lsst.shapelet.MultiShapeletBasis(size)
        basis.addComponent(1.0, function.getOrder(), numpy.identity(size))
        factoryF = lsst.shapelet.MatrixBuilderF.Factory(self.xF, self.yF, function.getOrder())
        factoryD = lsst.shapelet.MatrixBuilderD.Factory(self.xD, self.yD, function.getOrder())
        # we should get the same results with an appropriately simple MultiShapeletBasis
        compoundFactoryF = lsst.shapelet.MatrixBuilderF.Factory(self.xF, self.yF, basis)
        compoundFactoryD = lsst.shapelet.MatrixBuilderD.Factory(self.xD, self.yD, basis)
        self.checkAccessors(factoryF, size)
        self.checkAccessors(factoryD, size)
        self.checkAccessors(compoundFactoryF, size)
        self.checkAccessors(compoundFactoryD, size)
        builder1F = factoryF()
        builder1D = factoryD()
        self.checkAccessors(builder1F, size)
        self.checkAccessors(builder1D, size)
        workspaceF = lsst.shapelet.MatrixBuilderF.Workspace(factoryF.computeWorkspace())
        workspaceD = lsst.shapelet.MatrixBuilderD.Workspace(factoryD.computeWorkspace())
        builder2F = factoryF(workspaceF)
        builder2D = factoryD(workspaceD)
        self.assertEqual(workspaceF.getRemaining(), 0)
        self.assertEqual(workspaceD.getRemaining(), 0)
        self.checkAccessors(builder2F, size)
        self.checkAccessors(builder2D, size)
        builder3F = compoundFactoryF()
        builder3D = compoundFactoryD()
        self.checkAccessors(builder3F, size)
        self.checkAccessors(builder3D, size)
        matrix1F = builder1F(function.getEllipse())
        matrix1D = builder1D(function.getEllipse())
        matrix2F = builder2F(function.getEllipse())
        matrix2D = builder2D(function.getEllipse())
        matrix3F = builder3F(function.getEllipse())
        matrix3D = builder3D(function.getEllipse())
        self.assertClose(matrix1D, matrix2D, rtol=0.0, atol=0.0)  # same code, different workspace
        self.assertClose(matrix1F, matrix2F, rtol=0.0, atol=0.0)  # same code, different workspace
        self.assertClose(matrix1F, matrix3F, rtol=0.0, atol=0.0)  # same code, different construction pattern
        self.assertClose(matrix1D, matrix3D, rtol=0.0, atol=0.0)  # same code, different construction pattern
        self.assertClose(matrix1F, matrix2F, rtol=1E-7, atol=0.0) # same code, different precision
        # Finally, check against a completely different implementation (which is tested elsewhere)
        checkEvaluator = function.evaluate()
        checkVector = checkEvaluator(self.xD, self.yD)
        self.assertClose(numpy.dot(matrix1D, function.getCoefficients()), checkVector, rtol=1E-15)


def suite():
    """Returns a suite containing all the test cases in this module."""

    lsst.utils.tests.init()
    suites = []
    suites += unittest.makeSuite(MatrixBuilderTestCase)
    suites += unittest.makeSuite(lsst.utils.tests.MemoryTestCase)
    return unittest.TestSuite(suites)

def run(shouldExit=False):
    """Run the tests"""
    lsst.utils.tests.run(suite(), shouldExit)

if __name__ == "__main__":
    run(True)
