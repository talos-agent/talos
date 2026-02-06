SELECT
    n1.id AS NodeA,
    n2.id AS NodeB,
    (2 + 2 * COS(ABS(n1.phase - n2.phase))) AS Intensity
FROM PetrusNodes n1
CROSS JOIN PetrusNodes n2
WHERE n1.id < n2.id;
