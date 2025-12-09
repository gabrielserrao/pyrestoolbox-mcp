"""Comprehensive tests for geomechanics calculation tools."""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pyrestoolbox_mcp.tools.geomech_tools import *
from pyrestoolbox_mcp.models.geomech_models import *


class TestVerticalStress:
    """Test vertical stress (overburden) calculations."""

    def test_vertical_stress_onshore(self):
        """Test onshore vertical stress calculation."""
        request = VerticalStressRequest(
            depth=10000.0,
            water_depth=0.0,
            avg_density=144.0,
            water_density=64.0
        )
        result = geomech_vertical_stress(request)

        assert isinstance(result, dict)
        assert "value" in result
        assert "gradient" in result
        assert result["value"] > 0
        assert 0.9 < result["gradient"] < 1.1  # Typical onshore gradient
        print(f"✓ Onshore vertical stress: {result['value']:.1f} psi, gradient: {result['gradient']:.3f} psi/ft")

    def test_vertical_stress_offshore(self):
        """Test offshore vertical stress with water column."""
        request = VerticalStressRequest(
            depth=10000.0,
            water_depth=2000.0,
            avg_density=144.0,
            water_density=64.0
        )
        result = geomech_vertical_stress(request)

        assert result["value"] > 0
        # Offshore gradient should be lower due to water column
        assert 0.8 < result["gradient"] < 1.0
        print(f"✓ Offshore vertical stress: {result['value']:.1f} psi, gradient: {result['gradient']:.3f} psi/ft")


class TestPorePressure:
    """Test pore pressure calculations."""

    def test_eaton_sonic_overpressured(self):
        """Test Eaton's method with sonic data showing overpressure."""
        request = PorePressureEatonRequest(
            depth=10000.0,
            observed_value=100.0,  # Slower sonic = overpressured
            normal_value=70.0,
            overburden_psi=10400.0,
            eaton_exponent=3.0,
            method="sonic"
        )
        result = geomech_pore_pressure_eaton(request)

        assert result["value"] > 0
        assert result["gradient"] > 0.465  # Overpressured
        assert result["overpressure"] > 0
        print(f"✓ Eaton pore pressure: {result['value']:.1f} psi, gradient: {result['gradient']:.3f} psi/ft, overpressure: {result['overpressure']:.1f} psi")

    def test_eaton_resistivity(self):
        """Test Eaton's method with resistivity data."""
        request = PorePressureEatonRequest(
            depth=10000.0,
            observed_value=5.0,  # Low resistivity = overpressured
            normal_value=10.0,
            overburden_psi=10400.0,
            eaton_exponent=1.2,
            method="resistivity"
        )
        result = geomech_pore_pressure_eaton(request)

        assert result["value"] > 0
        assert result["gradient"] > 0
        print(f"✓ Eaton resistivity: {result['value']:.1f} psi, gradient: {result['gradient']:.3f} psi/ft")


class TestEffectiveStress:
    """Test effective stress calculations."""

    def test_effective_stress_scalar(self):
        """Test effective stress with scalar inputs."""
        request = EffectiveStressRequest(
            total_stress=10400.0,
            pore_pressure=4680.0,
            biot_coefficient=1.0
        )
        result = geomech_effective_stress(request)

        assert isinstance(result["value"], float)
        assert result["value"] == pytest.approx(5720.0, rel=0.01)
        print(f"✓ Effective stress: {result['value']:.1f} psi")

    def test_effective_stress_array(self):
        """Test effective stress with array inputs."""
        request = EffectiveStressRequest(
            total_stress=[10000.0, 10400.0, 10800.0],
            pore_pressure=[4500.0, 4680.0, 4860.0],
            biot_coefficient=0.9
        )
        result = geomech_effective_stress(request)

        assert isinstance(result["value"], list)
        assert len(result["value"]) == 3
        assert all(v > 0 for v in result["value"])
        print(f"✓ Effective stress (array): {result['value']}")


class TestHorizontalStress:
    """Test horizontal stress calculations."""

    def test_horizontal_stress_normal_faulting(self):
        """Test horizontal stress in normal faulting regime."""
        request = HorizontalStressRequest(
            vertical_stress=10400.0,
            pore_pressure=4680.0,
            poisson_ratio=0.25,
            tectonic_factor=0.0,
            biot_coefficient=1.0
        )
        result = geomech_horizontal_stress(request)

        assert result["sigma_h_min"] > 0
        assert result["sigma_h_max"] >= result["sigma_h_min"]
        assert result["stress_regime"] == "normal"
        print(f"✓ Horizontal stress (normal): σh_min={result['sigma_h_min']:.1f} psi, σh_max={result['sigma_h_max']:.1f} psi")

    def test_horizontal_stress_strike_slip(self):
        """Test horizontal stress in strike-slip regime."""
        request = HorizontalStressRequest(
            vertical_stress=10400.0,
            pore_pressure=4680.0,
            poisson_ratio=0.25,
            tectonic_factor=0.5,
            biot_coefficient=1.0
        )
        result = geomech_horizontal_stress(request)

        assert result["stress_regime"] == "strike-slip"
        print(f"✓ Horizontal stress (strike-slip): σh_min={result['sigma_h_min']:.1f} psi, σh_max={result['sigma_h_max']:.1f} psi")

    def test_horizontal_stress_reverse_faulting(self):
        """Test horizontal stress in reverse faulting regime."""
        request = HorizontalStressRequest(
            vertical_stress=10400.0,
            pore_pressure=4680.0,
            poisson_ratio=0.25,
            tectonic_factor=1.0,
            biot_coefficient=1.0
        )
        result = geomech_horizontal_stress(request)

        assert result["stress_regime"] == "reverse"
        print(f"✓ Horizontal stress (reverse): σh_min={result['sigma_h_min']:.1f} psi, σh_max={result['sigma_h_max']:.1f} psi")


class TestElasticModuli:
    """Test elastic moduli conversions."""

    def test_convert_E_and_nu(self):
        """Test conversion from Young's modulus and Poisson's ratio."""
        request = ElasticModuliRequest(
            youngs_modulus=1000000.0,
            poisson_ratio=0.25
        )
        result = geomech_elastic_moduli_conversion(request)

        assert all(k in result for k in ["youngs_modulus", "bulk_modulus", "shear_modulus", "poisson_ratio", "lame_parameter"])
        assert result["youngs_modulus"] == 1000000.0
        assert result["poisson_ratio"] == 0.25
        assert result["shear_modulus"] > 0
        assert result["bulk_modulus"] > 0
        print(f"✓ Elastic moduli: E={result['youngs_modulus']:.0f} psi, G={result['shear_modulus']:.0f} psi, K={result['bulk_modulus']:.0f} psi")

    def test_convert_K_and_G(self):
        """Test conversion from bulk and shear moduli."""
        request = ElasticModuliRequest(
            bulk_modulus=666667.0,
            shear_modulus=400000.0
        )
        result = geomech_elastic_moduli_conversion(request)

        assert result["youngs_modulus"] > 0
        assert 0 < result["poisson_ratio"] < 0.5
        print(f"✓ Elastic moduli from K,G: E={result['youngs_modulus']:.0f} psi, ν={result['poisson_ratio']:.3f}")


class TestRockStrength:
    """Test rock strength calculations."""

    def test_mohr_coulomb(self):
        """Test Mohr-Coulomb failure criterion."""
        request = RockStrengthRequest(
            cohesion=500.0,
            friction_angle=30.0,
            effective_stress_min=2000.0
        )
        result = geomech_rock_strength_mohr_coulomb(request)

        assert result["max_principal_stress"] > 0
        assert result["unconfined_strength"] > 0
        assert result["q_factor"] > 1.0  # Always > 1 for physical materials
        assert result["shear_strength"] > request.cohesion  # Should be larger with confining stress
        print(f"✓ Rock strength: UCS={result['unconfined_strength']:.1f} psi, σ1_failure={result['max_principal_stress']:.1f} psi, q={result['q_factor']:.2f}")


class TestDynamicToStatic:
    """Test dynamic to static moduli conversion."""

    def test_eissa_kazi(self):
        """Test Eissa-Kazi correlation for sandstone."""
        request = DynamicToStaticRequest(
            dynamic_youngs=1500000.0,
            dynamic_poisson=0.20,
            correlation="eissa_kazi",
            lithology="sandstone"
        )
        result = geomech_dynamic_to_static_moduli(request)

        assert result["static_youngs"] < request.dynamic_youngs  # Static should be lower
        assert result["static_poisson"] < request.dynamic_poisson
        assert 0.4 < result["correction_factor"] < 0.8
        print(f"✓ Dynamic to static: Edyn={request.dynamic_youngs:.0f} → Estat={result['static_youngs']:.0f} psi (factor={result['correction_factor']:.3f})")


class TestBreakoutWidth:
    """Test borehole breakout calculations."""

    def test_breakout_width_stable(self):
        """Test breakout calculation for stable wellbore."""
        request = BreakoutWidthRequest(
            sigma_h_max=8500.0,
            sigma_h_min=7500.0,  # Higher, more stable
            pore_pressure=4680.0,
            mud_weight=12.0,  # Higher MW
            wellbore_azimuth=45.0,
            ucs=3000.0,
            friction_angle=30.0
        )
        result = geomech_breakout_width(request)

        assert "breakout_width" in result
        assert "failure_status" in result
        assert result["breakout_width"] >= 0
        print(f"✓ Breakout width: {result['breakout_width']:.1f}°, status: {result['failure_status']}, critical MW: {result['critical_mud_weight']:.1f} ppg")

    def test_breakout_width_unstable(self):
        """Test breakout calculation for potentially unstable wellbore."""
        request = BreakoutWidthRequest(
            sigma_h_max=8500.0,
            sigma_h_min=6500.0,
            pore_pressure=4680.0,
            mud_weight=9.0,  # Lower MW, may cause breakout
            wellbore_azimuth=45.0,
            ucs=3000.0,
            friction_angle=30.0
        )
        result = geomech_breakout_width(request)

        assert result["breakout_width"] >= 0
        print(f"✓ Breakout width (low MW): {result['breakout_width']:.1f}°, status: {result['failure_status']}")


class TestFractureGradient:
    """Test fracture gradient calculations."""

    def test_fracture_gradient_eaton(self):
        """Test fracture gradient using Eaton method."""
        request = FractureGradientRequest(
            depth=10000.0,
            vertical_stress=10400.0,
            pore_pressure=4680.0,
            poisson_ratio=0.25,
            method="eaton"
        )
        result = geomech_fracture_gradient(request)

        assert result["fracture_pressure"] > request.pore_pressure
        assert 0.7 < result["fracture_gradient"] < 1.0  # Typical range
        assert result["equivalent_mud_weight"] > 0
        print(f"✓ Fracture gradient: {result['fracture_gradient']:.3f} psi/ft, Pfrac={result['fracture_pressure']:.1f} psi, EMW={result['equivalent_mud_weight']:.1f} ppg")

    def test_fracture_gradient_with_sigma_h_min(self):
        """Test fracture gradient with known minimum horizontal stress."""
        request = FractureGradientRequest(
            depth=10000.0,
            sigma_h_min=7800.0,
            vertical_stress=10400.0,
            pore_pressure=4680.0,
            method="hubbert_willis"
        )
        result = geomech_fracture_gradient(request)

        assert result["fracture_pressure"] == request.sigma_h_min
        print(f"✓ Fracture gradient (known σh): {result['fracture_gradient']:.3f} psi/ft")


class TestMudWeightWindow:
    """Test safe mud weight window calculations."""

    def test_mud_weight_window_wide(self):
        """Test wide mud weight window."""
        request = MudWeightWindowRequest(
            pore_pressure=4680.0,
            fracture_pressure=7800.0,
            depth=10000.0,
            safety_margin_overbalance=0.5,
            safety_margin_fracture=0.5
        )
        result = geomech_safe_mud_weight_window(request)

        assert result["max_mud_weight"] > result["min_mud_weight"]
        assert result["window_width"] > 0
        assert "wide" in result["status"] or "moderate" in result["status"]
        print(f"✓ Mud weight window: {result['min_mud_weight']:.1f}-{result['max_mud_weight']:.1f} ppg (width={result['window_width']:.1f} ppg, {result['status']})")

    def test_mud_weight_window_narrow(self):
        """Test narrow mud weight window."""
        request = MudWeightWindowRequest(
            pore_pressure=6000.0,  # Higher PP
            fracture_pressure=7000.0,  # Lower frac
            depth=10000.0,
            safety_margin_overbalance=0.5,
            safety_margin_fracture=0.5
        )
        result = geomech_safe_mud_weight_window(request)

        assert result["window_width"] >= 0  # May be narrow or negative
        print(f"✓ Mud weight window (narrow): {result['min_mud_weight']:.1f}-{result['max_mud_weight']:.1f} ppg (width={result['window_width']:.1f} ppg, {result['status']})")


class TestCriticalMudWeight:
    """Test critical mud weight for collapse prevention."""

    def test_critical_mud_weight(self):
        """Test critical mud weight calculation."""
        request = CriticalMudWeightRequest(
            sigma_h_max=8500.0,
            sigma_h_min=6500.0,
            pore_pressure=4680.0,
            cohesion=500.0,
            friction_angle=30.0,
            wellbore_azimuth=45.0,
            wellbore_inclination=0.0,
            depth=10000.0
        )
        result = geomech_critical_mud_weight_collapse(request)

        assert result["critical_mud_weight"] > 0
        assert result["collapse_pressure"] > request.pore_pressure
        print(f"✓ Critical mud weight: {result['critical_mud_weight']:.1f} ppg, collapse pressure: {result['collapse_pressure']:.1f} psi")


class TestReservoirCompaction:
    """Test reservoir compaction calculations."""

    def test_reservoir_compaction(self):
        """Test reservoir compaction from pressure depletion."""
        request = ReservoirCompactionRequest(
            pressure_drop=1000.0,
            reservoir_thickness=100.0,
            youngs_modulus=500000.0,
            poisson_ratio=0.25,
            biot_coefficient=1.0
        )
        result = geomech_reservoir_compaction(request)

        assert result["compaction"] > 0
        assert result["subsidence"] > 0
        assert result["subsidence"] < result["compaction"]  # Subsidence < compaction
        assert result["strain"] > 0
        print(f"✓ Reservoir compaction: {result['compaction']:.2f} ft, subsidence: {result['subsidence']:.2f} ft, strain: {result['strain']:.4f}")


class TestPoreCompressibility:
    """Test pore compressibility calculations."""

    def test_pore_compressibility_from_E_nu(self):
        """Test pore compressibility from elastic moduli."""
        request = PoreCompressibilityRequest(
            porosity=0.20,
            youngs_modulus=500000.0,
            poisson_ratio=0.25,
            grain_compressibility=3e-7
        )
        result = geomech_pore_compressibility(request)

        assert result["pore_compressibility"] > 0
        assert result["bulk_compressibility"] > 0
        assert result["pore_compressibility"] > result["bulk_compressibility"]  # Cf > Cb
        print(f"✓ Pore compressibility: {result['pore_compressibility']:.2e} 1/psi, Cb: {result['bulk_compressibility']:.2e} 1/psi")

    def test_pore_compressibility_from_Cb(self):
        """Test pore compressibility from known bulk compressibility."""
        request = PoreCompressibilityRequest(
            bulk_compressibility=2e-6,
            porosity=0.20,
            grain_compressibility=3e-7
        )
        result = geomech_pore_compressibility(request)

        assert result["pore_compressibility"] > 0
        print(f"✓ Pore compressibility (from Cb): {result['pore_compressibility']:.2e} 1/psi")


class TestLeakOffPressure:
    """Test leak-off test analysis."""

    def test_leak_off_test(self):
        """Test LOT analysis."""
        request = LeakOffPressureRequest(
            leak_off_pressure=2500.0,
            mud_weight=9.0,
            test_depth=10000.0,
            pore_pressure=4680.0,
            test_type="LOT"
        )
        result = geomech_leak_off_pressure(request)

        assert result["sigma_h_min"] > 0
        assert result["sigma_h_min"] > request.pore_pressure
        assert result["fracture_gradient"] > 0
        assert result["breakdown_pressure"] is not None
        print(f"✓ LOT analysis: σh_min={result['sigma_h_min']:.1f} psi, gradient={result['fracture_gradient']:.3f} psi/ft, EMW={result['equivalent_mud_weight']:.1f} ppg")

    def test_formation_integrity_test(self):
        """Test FIT analysis."""
        request = LeakOffPressureRequest(
            leak_off_pressure=2000.0,
            mud_weight=9.0,
            test_depth=10000.0,
            pore_pressure=4680.0,
            test_type="FIT"
        )
        result = geomech_leak_off_pressure(request)

        assert result["sigma_h_min"] > 0
        assert result["breakdown_pressure"] is None  # FIT doesn't fracture
        print(f"✓ FIT analysis: σh_min ≥ {result['sigma_h_min']:.1f} psi (lower bound)")


class TestFractureWidth:
    """Test hydraulic fracture width calculations."""

    def test_fracture_width_pkn(self):
        """Test PKN fracture width model."""
        request = FractureWidthRequest(
            net_pressure=500.0,
            fracture_height=100.0,
            fracture_half_length=500.0,
            youngs_modulus=1000000.0,
            poisson_ratio=0.25,
            model="PKN"
        )
        result = geomech_hydraulic_fracture_width(request)

        assert result["avg_width"] > 0
        assert result["max_width"] > result["avg_width"]
        assert result["model_used"] == "PKN"
        print(f"✓ Fracture width (PKN): avg={result['avg_width']:.3f} in, max={result['max_width']:.3f} in")

    def test_fracture_width_kgd(self):
        """Test KGD fracture width model."""
        request = FractureWidthRequest(
            net_pressure=500.0,
            fracture_height=100.0,
            fracture_half_length=500.0,
            youngs_modulus=1000000.0,
            poisson_ratio=0.25,
            model="KGD"
        )
        result = geomech_hydraulic_fracture_width(request)

        assert result["avg_width"] > 0
        assert result["max_width"] > result["avg_width"]
        assert result["model_used"] == "KGD"
        print(f"✓ Fracture width (KGD): avg={result['avg_width']:.3f} in, max={result['max_width']:.3f} in")


def run_all_tests():
    """Run all geomechanics tests and report results."""
    print("\n" + "="*80)
    print("GEOMECHANICS TOOLS COMPREHENSIVE TEST SUITE")
    print("="*80 + "\n")

    test_classes = [
        TestVerticalStress,
        TestPorePressure,
        TestEffectiveStress,
        TestHorizontalStress,
        TestElasticModuli,
        TestRockStrength,
        TestDynamicToStatic,
        TestBreakoutWidth,
        TestFractureGradient,
        TestMudWeightWindow,
        TestCriticalMudWeight,
        TestReservoirCompaction,
        TestPoreCompressibility,
        TestLeakOffPressure,
        TestFractureWidth,
    ]

    total_tests = 0
    passed_tests = 0
    failed_tests = []

    for test_class in test_classes:
        print(f"\n{test_class.__name__}")
        print("-" * 80)

        test_instance = test_class()
        test_methods = [method for method in dir(test_instance) if method.startswith('test_')]

        for method_name in test_methods:
            total_tests += 1
            try:
                method = getattr(test_instance, method_name)
                method()
                passed_tests += 1
            except Exception as e:
                failed_tests.append((test_class.__name__, method_name, str(e)))
                print(f"✗ {method_name} FAILED: {str(e)}")

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(failed_tests)}")

    if failed_tests:
        print("\nFailed tests:")
        for class_name, method_name, error in failed_tests:
            print(f"  - {class_name}.{method_name}: {error}")
        return False
    else:
        print("\n🎉 ALL GEOMECHANICS TOOLS PASSED! 🎉")
        return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
