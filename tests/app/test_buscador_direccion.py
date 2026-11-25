"""La ficha enseña lo que llega por la dirección salvo que se acabe de elegir otra cosa en su
buscador (D-058). Antes lo elegido una vez en el buscador tapaba todo lo que llegaba después."""

from streamlit.testing.v1 import AppTest


def _app():
    import streamlit as st

    from ojo_ciudadano.app import buscador

    st.session_state["visto"] = buscador.con_direccion(
        st.session_state.get("buscado"), "empresa", "prueba"
    )


def test_la_direccion_manda_salvo_una_eleccion_nueva():
    at = AppTest.from_function(_app)
    # se elige una empresa en el buscador de la ficha: se ve y pasa a la dirección
    at.session_state["buscado"] = "FRESENIUS"
    at.run()
    assert at.session_state["visto"] == "FRESENIUS"
    assert at.query_params["empresa"] == "FRESENIUS"
    # se llega desde el Inicio con otra empresa en la dirección: manda la dirección
    at.query_params["empresa"] = "FERROVIAL"
    at.run()
    assert at.session_state["visto"] == "FERROVIAL"
    # se elige otra en el buscador de la ficha: manda la nueva elección
    at.session_state["buscado"] = "TELEFONICA"
    at.run()
    assert at.session_state["visto"] == "TELEFONICA"
