"""Nox Sessions."""
import tempfile
from pathlib import Path

import nox

locations = "src", "tests", "noxfile.py", "docs/conf.py", "examples"
nox.options.sessions = "safety", "tests", "xdoctest"


def install_with_constraints(session, *args, **kwargs):
    """Install packages constrained by Poetry's lock file."""
    with tempfile.TemporaryDirectory() as directory:
        requirements = Path(directory) / "requirements.txt"
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            f"--output={requirements}",
            external=True,
        )
        session.install(f"--constraint={requirements}", *args, **kwargs)


@nox.session()
def tests(session):
    """Run the test suite."""
    args = session.posargs or ["--cov", "-m", "not e2e"]
    session.run("poetry", "install", external=True)
    install_with_constraints(session, "coverage[toml]", "pytest", "pytest-cov")
    session.run("pytest", *args)


@nox.session()
def coverage(session):
    """Upload coverage data."""
    install_with_constraints(session, "coverage[toml]", "codecov")
    session.run("coverage", "xml", "--fail-under=0")
    session.run("codecov", *session.posargs)


@nox.session()
def xdoctest(session):
    """Run examples with xdoctest."""
    args = session.posargs or ["all"]
    session.run("poetry", "install", "--no-dev", external=True)
    install_with_constraints(session, "xdoctest")
    session.run("python", "-m", "xdoctest", "seaborn_image", *args)


@nox.session()
def lint(session):
    """Lint using flake8."""
    args = session.posargs or locations
    install_with_constraints(
        session,
        "flake8",
        "flake8-black",
        "flake8-bugbear",
        "flake8-bandit",
        "flake8-docstrings",
    )
    session.run("flake8", *args)


@nox.session()
def black(session):
    """Run black code formatter."""
    args = session.posargs or locations
    install_with_constraints(session, "black")
    session.run("black", *args)


@nox.session()
def safety(session):
    """Scan dependencies for insecure packages."""
    with tempfile.TemporaryDirectory() as directory:
        requirements = Path(directory) / "requirements.txt"
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            f"--output={requirements}",
            external=True,
        )
        install_with_constraints(session, "safety")
        session.run("safety", "check", f"--file={requirements}", "--full-report")


@nox.session()
def docs(session):
    """Build the documentation."""
    session.run("poetry", "install", external=True)
    install_with_constraints(session, "sphinx")
    session.run("sphinx-build", "docs", "docs/_build")
