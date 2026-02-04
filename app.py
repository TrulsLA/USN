import math
from dataclasses import dataclass
from typing import Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

st.set_page_config(page_title="Polar-koordinater", layout="centered")


ALLOWED_NAMES: Dict[str, object] = {
    "np": np,
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "arcsin": np.arcsin,
    "arccos": np.arccos,
    "arctan": np.arctan,
    "exp": np.exp,
    "sqrt": np.sqrt,
    "log": np.log,
    "log10": np.log10,
    "pi": np.pi,
    "e": np.e,
    "abs": np.abs,
}


@dataclass
class PolarFunction:
    label: str
    expression: str
    enabled: bool


DEFAULT_FUNCTIONS = [
    PolarFunction("Funksjon 1", "2 + 0.5*sin(3*theta)", True),
    PolarFunction("Funksjon 2", "1 + cos(2*theta)", False),
    PolarFunction("Funksjon 3", "0.5 + 0.2*sin(5*theta)", False),
]


def safe_eval(expression: str, theta: np.ndarray) -> np.ndarray:
    if not expression.strip():
        raise ValueError("Uttrykket kan ikke være tomt.")
    local_vars = {"theta": theta}
    return eval(expression, {"__builtins__": {}}, {**ALLOWED_NAMES, **local_vars})


def cartesian_to_polar(x: float, y: float) -> Tuple[float, float]:
    r = math.hypot(x, y)
    theta = math.atan2(y, x)
    return r, theta


def polar_to_cartesian(r: float, theta: float) -> Tuple[float, float]:
    x = r * math.cos(theta)
    y = r * math.sin(theta)
    return x, y


st.title("Polare koordinater")
st.write(
    "Skriv inn funksjoner for r(θ), slå dem av/på, og konverter mellom kartesiske "
    "og polare koordinater."
)

with st.expander("Tips til funksjonsuttrykk", expanded=False):
    st.markdown(
        "**Eksempler:** `2 + 0.5*sin(3*theta)` · `1 + cos(2*theta)` · `sqrt(theta)`  \n"
        "Du kan bruke funksjoner som `sin`, `cos`, `tan`, `sqrt`, `exp`, `log` og `pi`."
    )

col_left, col_right = st.columns([2, 1], gap="large")

with col_left:
    st.subheader("Funksjoner")
    function_inputs = []
    for idx, default in enumerate(DEFAULT_FUNCTIONS, start=1):
        with st.container():
            enabled = st.checkbox(
                f"Vis {default.label}",
                value=default.enabled,
                key=f"enabled_{idx}",
            )
            expression = st.text_input(
                f"r(θ) for {default.label}",
                value=default.expression,
                key=f"expr_{idx}",
                help="Skriv uttrykket i Python-syntaks, f.eks. 2 + 0.5*sin(3*theta)",
            )
            function_inputs.append(PolarFunction(default.label, expression, enabled))

    st.subheader("Grafinnstillinger")
    theta_min, theta_max = st.slider(
        "θ-område (radianer)",
        min_value=0.0,
        max_value=float(2 * np.pi),
        value=(0.0, float(2 * np.pi)),
        step=0.1,
    )
    resolution = st.slider("Antall punkter", min_value=200, max_value=2000, value=600, step=100)

with col_right:
    st.subheader("Konvertering")
    unit = st.radio("Vinkel-enhet", ["Radianer", "Grader"], horizontal=True)
    st.markdown("**Kartesisk → Polar**")
    x_value = st.number_input("x", value=1.0, format="%.3f")
    y_value = st.number_input("y", value=1.0, format="%.3f")
    r_value, theta_value = cartesian_to_polar(x_value, y_value)
    theta_display = math.degrees(theta_value) if unit == "Grader" else theta_value
    st.write(f"r = **{r_value:.3f}**, θ = **{theta_display:.3f}**")

    st.markdown("**Polar → Kartesisk**")
    r_input = st.number_input("r", value=2.0, format="%.3f")
    theta_input = st.number_input("θ", value=1.0, format="%.3f")
    theta_radians = math.radians(theta_input) if unit == "Grader" else theta_input
    x_out, y_out = polar_to_cartesian(r_input, theta_radians)
    st.write(f"x = **{x_out:.3f}**, y = **{y_out:.3f}**")

st.subheader("Polar-plot")

if theta_max <= theta_min:
    st.error("θ-maks må være større enn θ-min.")
else:
    theta = np.linspace(theta_min, theta_max, resolution)
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection="polar")

    plotted = False
    for func in function_inputs:
        if not func.enabled:
            continue
        try:
            r_values = safe_eval(func.expression, theta)
            ax.plot(theta, r_values, label=func.label)
            plotted = True
        except Exception as exc:  # noqa: BLE001
            st.warning(f"Kunne ikke tegne {func.label}: {exc}")

    ax.set_title("Polare funksjoner")
    if plotted:
        ax.legend(loc="upper right", bbox_to_anchor=(1.2, 1.1))
    ax.grid(True)

    st.pyplot(fig, clear_figure=True)
