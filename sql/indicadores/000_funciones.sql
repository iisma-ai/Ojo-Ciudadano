-- Funciones auxiliares que usan los indicadores. El ejecutor las crea antes de lanzarlos.

-- Importe con formato español: 18150 -> '18.150,00'.
CREATE OR REPLACE MACRO euros(x) AS
    replace(replace(replace(format('{:,.2f}', CAST(x AS DOUBLE)), ',', '_'), '.', ','), '_', '.');
