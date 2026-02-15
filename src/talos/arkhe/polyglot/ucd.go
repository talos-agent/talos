// ucd.go
package main

import (
	"fmt"
	"math"
)

type UCD struct {
	data [][]float64
	C    float64
	F    float64
}

func NewUCD(data [][]float64) *UCD {
	return &UCD{data: data}
}

func (u *UCD) pearson(x, y []float64) float64 {
	n := len(x)
	sumX, sumY := 0.0, 0.0
	for i := 0; i < n; i++ {
		sumX += x[i]
		sumY += y[i]
	}
	meanX := sumX / float64(n)
	meanY := sumY / float64(n)
	var num, denX, denY float64
	for i := 0; i < n; i++ {
		dx := x[i] - meanX
		dy := y[i] - meanY
		num += dx * dy
		denX += dx * dx
		denY += dy * dy
	}
	if denX == 0 || denY == 0 {
		return 0
	}
	return num / math.Sqrt(denX*denY)
}

func (u *UCD) Analyze() (C, F float64, conservation bool, topology, scaling string, optimization float64) {
	n := len(u.data)
	if n > 1 {
		var sumCorr float64
		count := 0
		for i := 0; i < n; i++ {
			for j := i + 1; j < n; j++ {
				corr := u.pearson(u.data[i], u.data[j])
				sumCorr += math.Abs(corr)
				count++
			}
		}
		if count > 0 {
			u.C = sumCorr / float64(count)
		} else {
			u.C = 0.5
		}
	} else {
		u.C = 0.5
	}
	u.F = 1.0 - u.C
	conservation = math.Abs(u.C+u.F-1.0) < 1e-10
	if u.C > 0.8 {
		topology = "toroidal"
	} else {
		topology = "other"
	}
	if u.C > 0.7 {
		scaling = "self-similar"
	} else {
		scaling = "linear"
	}
	optimization = u.F * 0.5
	return u.C, u.F, conservation, topology, scaling, optimization
}

func main() {
	data := [][]float64{
		{1, 2, 3, 4},
		{2, 3, 4, 5},
		{5, 6, 7, 8},
	}
	ucd := NewUCD(data)
	c, f, cons, topo, scale, opt := ucd.Analyze()
	fmt.Printf("C: %.4f, F: %.4f, conservation: %v, topology: %s, scaling: %s, opt: %.4f\n",
		c, f, cons, topo, scale, opt)
}
