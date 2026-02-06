(defstruct petrus-node id phase)

(defun diffract (node-a node-b)
  (let* ((delta (abs (- (petrus-node-phase node-a)
                        (petrus-node-phase node-b))))
         (intensity (+ 2 (* 2 (cos delta)))))
    (cond ((> intensity 3.4) 'constructive)
          ((< intensity 0.6) 'destructive)
          (t 'quadrature))))
