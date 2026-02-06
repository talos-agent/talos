module Petrus where

type Phase = Double
data Regime = Constructive | Destructive | Quadrature deriving (Show, Eq)

interference :: Phase -> Phase -> Regime
interference phiA phiB
    | cos delta > 0.7  = Constructive
    | cos delta < -0.7 = Destructive
    | otherwise        = Quadrature
    where delta = abs (phiA - phiB)
