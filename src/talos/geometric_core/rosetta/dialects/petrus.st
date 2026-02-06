Object subclass: #PetrusNode
    instanceVariableNames: 'phase'

!PetrusNode methodsFor: 'physics'!
interfereWith: anotherNode
    | delta |
    delta := (self phase - anotherNode phase) abs.
    (delta cos > 0.7) ifTrue: [^ 'Constructive'].
    ^ 'Quadrature'
