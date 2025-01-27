# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 13:24:21 2023

@author: C43353
"""

import zipfile
import pandas as pd
from scipy import interpolate
import numpy as np
import matplotlib.pyplot as plt
from Functions import nodal, forces, nodal_chord

"""
BEM for 15 MW Wind Turbine

Code takes the number of blades, radius and tip speed ratio for turbine.
Set the variation of wind speeds, segmental positions and global pitch angles.

An optimum blade profile will be generated with chord and twist distribution
for a wind speed of 10 m/s.

This blade will then undergo BEM theory to produce force distributions,
power outputs etc.

This is then plotted to allow easier comprehension.

Notes -
Not sure if final segmental force and torque plots are correct (have just
removed the lowest radial node to allow plotting)
"""


""" Constants """
rho = 1.225  # Air Density (kg/m^3)

B = 3  # Number of Blades
N = 17  # Number of Elements

R = 115  # Radius (m)

# omega = 2.83  # Angular Veolcity (rad/s) (Constant for varying wind speeds)
tsr = 7  # Tip Speed Ratio (Used to define the angular velocity)
omega = (tsr * 10) / R  # Angular Velocity (dependent on tip speed ratio)


""" Variables """
# Wind Speeds (m/s)
speeds = np.linspace(5, 20, 31)

# Radial Position of Nodes (m)
segments = np.linspace(2, R-0.2, N)
# segments = np.array([2, 4, 6, 10, 16,
#                      22, 28, 34, 40, 46,
#                      52, 58, 64, 70, 76,
#                      80, 84.8])

# Global Pitch Angle
thetaps = np.array([20, 16, 12, 8, 5, 0])


""" Rank Airfoils, Find Optimum Angle of Attack """
# Create dictionaries to store data
data = {}
maxcld = {}

# Define the zipfile that stores all the cld data CSVs
zf = zipfile.ZipFile("Aerofoil-data.zip")

for number in range(51):
    # Force the number to be 0x for 0-9
    filenumb = f"{number:02d}"
    name2 = "Profile-" + filenumb + "-CLD.csv"
    df2 = pd.read_csv(zf.open(name2), header=None)
    df2 = df2[pd.to_numeric(df2[0], errors="coerce").notnull()]
    df2 = {0: pd.to_numeric(df2[0]),
           1: pd.to_numeric(df2[1]),
           2: pd.to_numeric(df2[2])}
    data[number] = pd.DataFrame(df2)

    data[number][3] = data[number][1] / data[number][2]

    maxcld[number] = data[number].loc[data[number][3].idxmax()]

maxcld = {key: val for key, val in sorted(maxcld.items(),
                                          key=lambda ele: ele[1][3])}

# Select every 3rd profile starting at element 3 (profile 42)
profilescld = list(maxcld.items())[2::3]

# Create a list of the profiles for the turbine
profiles = [x[0] for x in profilescld]

# Create a list of the optimum angle of attacks for the profiles
aoa = [x[1][0] for x in profilescld]


"""
Calculate Twist Angles and Chord Length for Blade
Using Optimum Angle of Attack
"""
thetas = []
chords = []
for m, r in enumerate(segments):
    V0 = 10  # m/s Nominal Wind Speed
    # c = chords[m]  # Chord Length from list
    alpha = aoa[m]  # Twist Angle from list

    profile = profiles[m]  # Profile Cross section from list
    # Create a function to interpolate to find Cl and Cd
    fcl = interpolate.interp1d(data[profile][0], data[profile][1])
    fcd = interpolate.interp1d(data[profile][0], data[profile][2])

    theta, chord = nodal_chord(R, r, V0, alpha, omega, B, rho, fcl, fcd)

    thetas.append(theta)
    chords.append(chord)

# Mirror the chord lengths about the third in the list for realistic sizes
original_chords = list(chords)
chords[0] = int(chords[2])
chords[1] = (chords[2] + chords[0]) / 2


""" Perform Calculations Over Varying Global Pitch Angles """
# Initialise the lists for pitch angle output lists
phi_final = []
alpha_final = []
Cl_final = []
Cd_final = []
Cn_final = []
Cr_final = []
F_final = []
aa_final = []
ar_final = []
fn_final = []
fr_final = []
Vrel_final = []
Ct_final = []
Cpinit_final = []
T_final = []
tau_final = []
P_final = []
Cp_final = []

# Calculations for all global pitch angles (thetaps)
for i, thetap in enumerate(thetaps):

    # Initialise the lists for the wind speed output lists
    phi_out = []
    alpha_out = []
    Cl_out = []
    Cd_out = []
    Cn_out = []
    Cr_out = []
    F_out = []
    aa_out = []
    ar_out = []
    fn_out = []
    fr_out = []
    Vrel_out = []
    Ct_out = []
    Cpinit_out = []
    T_out = []
    tau_out = []
    P_out = []
    Cp_out = []
    tsr_out = []

    # Add fixed pitch angle to varying pitch angle
    pitch = thetas + thetap

    """ Perform Calculations Over Varying Wind Speeds """
    # Perform calculations over wind speeds (speeds)
    for n, V0 in enumerate(speeds):

        # Initialise the lists for the radial outputs
        phi_list = []
        alpha_list = []
        Cl_list = []
        Cd_list = []
        Cn_list = []
        Cr_list = []
        F_list = []
        aa_list = []
        ar_list = []
        fn_list = []
        fr_list = []
        Vrel_list = []
        Ct_list = []
        Cpinit_list = []
        T = []
        tau = []

        """ Perform Calculations Over Radial Position on Blade"""
        # Perform the calculations over the radial positions (segments)
        for m, r in enumerate(segments):
            c = chords[m]  # Chord Length from list
            theta = pitch[m]  # Twist Angle from list

            profile = profiles[m]  # Profile Cross section from list
            # Create a function to interpolate to find Cl and Cd
            fcl = interpolate.interp1d(data[profile][0], data[profile][1])
            fcd = interpolate.interp1d(data[profile][0], data[profile][2])

            # Use nodal function to calculate outputs for radial position
            phi, alpha, Cl, Cd, Cn, Cr, F, aa, ar, fn, fr, Vrel, Ct, Cpinit = \
                nodal(R, r, V0, c, theta, omega, B, rho, fcl, fcd)

            # Append the outputs for radial position to lists
            phi_list.append(phi)
            alpha_list.append(alpha)
            Cl_list.append(Cl)
            Cd_list.append(Cd)
            Cn_list.append(Cn)
            Cr_list.append(Cr)
            F_list.append(F)
            aa_list.append(aa)
            ar_list.append(ar)
            fn_list.append(fn)
            fr_list.append(fr)
            Vrel_list.append(Vrel)
            Ct_list.append(Ct)
            Cpinit_list.append(Cpinit)

        """ Calculate Turbine Outputs """
        # Use forces function to calculate the normal force and torque on blade
        T, tau = forces(segments, fn_list, fr_list)

        # Calculate the power output of the turbine
        P = B * omega * sum(tau)

        # Calculate the power coefficient of the turbine
        Cp = P / ((1/2) * np.pi * rho * (R ** 2) * (V0 ** 3))

        # Append the outputs for wind speed to lists
        phi_out.append(phi_list)
        alpha_out.append(alpha_list)
        Cl_out.append(Cl_list)
        Cd_out.append(Cd_list)
        Cn_out.append(Cn_list)
        Cr_out.append(Cr_list)
        F_out.append(F_list)
        aa_out.append(aa_list)
        ar_out.append(ar_list)
        fn_out.append(fn_list)
        fr_out.append(fr_list)
        Vrel_out.append(Vrel_list)
        Ct_out.append(Ct_list)
        Cpinit_out.append(Cpinit_list)
        T_out.append(T)
        tau_out.append(tau)
        P_out.append(P)
        Cp_out.append(Cp)
        tsr_out.append((omega * R) / V0)  # Tip Speed Ratio)

    phi_final.append(phi_out)
    alpha_final.append(alpha_out)
    Cl_final.append(Cl_out)
    Cd_final.append(Cd_out)
    Cn_final.append(Cn_out)
    Cr_final.append(Cr_out)
    F_final.append(F_out)
    aa_final.append(aa_out)
    ar_final.append(ar_out)
    fn_final.append(fn_out)
    fr_final.append(fr_out)
    Vrel_final.append(Vrel_out)
    Ct_final.append(Ct_out)
    Cpinit_final.append(Cpinit_out)
    T_final.append(T_out)
    tau_final.append(tau_out)
    P_final.append(P_out)
    Cp_final.append(Cp_out)


""" Plots To Compare to Lectures """

v = 10  # (The location in speeds containing desired wind speed)
# Plot the nodal forces against radial position (v = 9 gives V0 = 9.5 m/s)
plt.figure(1, figsize=(6, 6))
plt.plot(segments, np.array(fn_out[v])/1E3, marker='o')
plt.plot(segments, np.array(fr_out[v])/1E3, marker='o')
plt.title((f"Nodal Force (V0 = {speeds[v]} m/s)"))
plt.xlabel(r"$r_i$, m")
# plt.xlim(4.5, 20.5)
plt.ylabel(r"$f_{N,i}$, $f_{R,i}$, kN/m")
# plt.ylim(0, 1.8)
plt.legend(labels=[r"$f_{N,i}$", r"$f_{R,i}$"])
plt.show()

# Plot the normal force and torque against segmental speed ratio (V0 = 9.5 m/s)
plt.figure(1, figsize=(6, 6))
plt.plot((omega * np.array(segments[-(len(segments)-1):])) / speeds[9],
         np.array(T_out[v])/1E3, marker='o')
plt.plot((omega * np.array(segments[-(len(segments)-1):])) / speeds[9],
         np.array(tau_out[v])/1E3, marker='o')
plt.title(f"Segmental Forces (V0 = {speeds[v]} m/s)")
plt.xlabel(r"$\xi$$_i$ = $\Omega$$r_i$/$V_0$")
# plt.xlim(1, 6.05)
plt.ylabel(r"$\tau$$_i$, kNm; $T_i$, kN")
# plt.ylim(0, 3.5)
plt.legend(labels=["$T_i$", r"$\tau$$_i$"])
plt.show()

# Plot Induction Factor in 3D
X, Y = np.meshgrid(segments, speeds)
fig = plt.figure()
ax = plt.axes(projection='3d')
ax.contour3D(Y, X, aa_out, 100)
ax.set_xlabel('Speeds (m/s)')
ax.set_ylabel('Segments (m)')
ax.set_zlabel('Induction Factor')
plt.show()


# Plot Angular Induction Factor in 3D
X, Y = np.meshgrid(segments, speeds)
fig = plt.figure()
ax = plt.axes(projection='3d')
ax.contour3D(Y, X, ar_out, 100)
ax.set_xlabel('Speeds (m/s)')
ax.set_ylabel('Segments (m)')
ax.set_zlabel('Radial Induction Factor')
ax.invert_xaxis()
ylim = ax.get_ylim()
ax.set_yticks(ax.get_yticks())
ax.set_ylim(ylim[::-1])
plt.show()

# # Plot the power output against wind speed
# plt.figure(1, figsize=(6, 6))
# plt.plot(speeds, np.array(P_out) * 1E-6, marker='o')
# plt.title("Power")
# plt.xlabel("Wind Speed (m/s)")
# plt.xlim(min(speeds), max(speeds))
# plt.ylabel("Power Output (MW)")
# plt.ylim(0, 10)
# plt.axhline(8, color="black", linestyle="--")
# plt.show()

# # Plot the power coefficient against wind speed
# plt.figure(1, figsize=(6, 6))
# plt.plot(speeds, Cp_out, marker='o')
# plt.title("Power Coefficient")
# plt.xlabel("Wind Speed (m/s)")
# plt.xlim(min(speeds), max(speeds))
# plt.ylabel("Power Coefficient")
# plt.ylim(0, 0.5)
# plt.show()

# # Plot the normalised power coefficient against tip speed ratio
# plt.figure(1, figsize=(6, 6))
# plt.plot(((omega*R)/np.array(speeds)),
#          (np.array(Cp_out)*(27/16)), marker='o')
# plt.title("Normalised")
# plt.xlabel(r"$\lambda$ = $\Omega$R/V$_0$ (Tip Speed Ratio)")
# # plt.xlim(2, 12)
# plt.ylabel("C$_p$ $\\times$ 27/16 (Normalised Power Coefficient)")
# plt.ylim(0, 1)
# plt.show()

# Plot the power output against wind speed for all global pitch angles
plt.figure(1, figsize=(6, 6))
for i in range(len(P_final)):
    plt.plot(speeds, np.array(list(reversed(P_final)))[i]/1E6)
plt.title("Power Against Wind Speed")
plt.xlabel(r"$V_0$, m/s")
plt.xlim(min(speeds), max(speeds))
plt.ylabel("P, MW")
plt.ylim(0, 30)
plt.axhline(15, color="black", linestyle="--")
plt.axvline(10, color="black", linestyle="--")
plt.legend(labels=[r"$\theta$$_p$ = 0",
                   r"$\theta$$_p$ = 5",
                   r"$\theta$$_p$ = 8",
                   r"$\theta$$_p$ = 12",
                   r"$\theta$$_p$ = 16",
                   r"$\theta$$_p$ = 20"])
plt.show()

# Plot the power coefficient against wind speed for all global pitch angles
plt.figure(1, figsize=(6, 6))
for i in range(len(Cp_final)):
    plt.plot(speeds, np.array(list(reversed(Cp_final)))[i])
plt.title("Power Coefficient Against Wind Speed")
plt.xlabel(r"$V_0$, m/s")
plt.xlim(min(speeds), max(speeds))
plt.ylabel("Cp")
plt.ylim(0, 0.5)
plt.legend(labels=[r"$\theta$$_p$ = 0",
                   r"$\theta$$_p$ = 5",
                   r"$\theta$$_p$ = 8",
                   r"$\theta$$_p$ = 12",
                   r"$\theta$$_p$ = 16",
                   r"$\theta$$_p$ = 20"])
plt.show()

# Plot power coefficient against tip speed ratio for all global pitch angles
plt.figure(1, figsize=(6, 6))
for i in range(len(Cp_final)):
    plt.plot(((omega*R)/np.array(speeds)),
             (np.array(list(reversed(Cp_final))[i])*(27/16)), marker='o')
    plt.title("Normalised")
    plt.xlabel(r"$\lambda$ = $\Omega$R/V$_0$ (Tip Speed Ratio)")
    # plt.xlim(2, 12)
    plt.ylabel("C$_p$ $\\times$ 27/16 (Normalised Power Coefficient)")
    plt.ylim(0, 1)
    plt.legend(labels=[r"$\theta$$_p$ = 0",
                       r"$\theta$$_p$ = 5",
                       r"$\theta$$_p$ = 8",
                       r"$\theta$$_p$ = 12",
                       r"$\theta$$_p$ = 16",
                       r"$\theta$$_p$ = 20"])
plt.show()

# Plot the normal force against power output for all global pitch angles
plt.figure(1, figsize=(6, 6))
for i in range(len(P_final)):
    plt.plot(np.array(list(reversed(P_final)))[i]/1E6,
             np.sum(list(reversed(T_final))[i], 1)/1E3)
plt.title("Normal Force Against Power Output")
plt.xlabel("P, MW")
plt.xlim(0, 30)
plt.ylabel("T, kN")
# plt.ylim(0, 8)
plt.ylim(bottom=0)
plt.axvline(15, color="black", linestyle="--")
plt.legend(labels=[r"$\theta$$_p$ = 0",
                   r"$\theta$$_p$ = 5",
                   r"$\theta$$_p$ = 8",
                   r"$\theta$$_p$ = 12",
                   r"$\theta$$_p$ = 16",
                   r"$\theta$$_p$ = 20"])
plt.show()

# Plot the chord length against radial position
plt.figure(1, figsize=(12, 6))
plt.title("Blade Distribution", fontsize=20)
plt.plot(segments, chords, marker="o")
plt.plot(segments, np.array(thetas)/10, marker="o")
plt.xlabel("$r_i$, m", fontsize=15)
plt.ylabel(r"$c_i$, m; $\theta$$_i$/10$\degree$", fontsize=15)
plt.show()


""" Non Lecture Plots """

# # Plot Prandtl Loss Factor on contour
# plt.figure(1, figsize=(12, 6))
# plt.contourf(segments, speeds, F_out, 50, cmap="gist_earth_r")
# plt.xlabel("Radial Position / m")
# plt.ylabel("Wind Speed / ms$^-$$^1$")
# plt.colorbar(label="Prandtl Loss Factor")
# plt.show()

# # Plot Angle of Attack on contour
# plt.figure(1, figsize=(12, 6))
# plt.contourf(segments, speeds, alpha_out, 50, cmap="gist_earth_r")
# plt.xlabel("Radial Position / m")
# plt.ylabel("Wind Speed / ms$^-$$^1$")
# plt.colorbar(label=r"Angle of Attack ($\alpha$) / deg")
# plt.show()

# # Plot Relative Wind Angle on contour
# plt.figure(1, figsize=(12, 6))
# plt.contourf(segments, speeds, phi_out, 50, cmap="gist_earth_r")
# plt.xlabel("Radial Position / m")
# plt.ylabel("Wind Speed / ms$^-$$^1$")
# plt.colorbar(label=r"Relative Wind Angle ($\phi$) / rad")
# plt.show()

# # Plot Normal Nodal Force on contour
# plt.figure(1, figsize=(12, 6))
# plt.contourf(segments, speeds, np.array(fn_out)/1000,
#              50, cmap="gist_earth_r")
# plt.xlabel("Radial Position / m")
# plt.ylabel("Wind Speed / ms$^-$$^1$")
# plt.colorbar(label="Normal Nodal Force (kN/m)")
# plt.show()

# # Plot Rotational Nodal Force on contour
# plt.figure(1, figsize=(12, 6))
# plt.contourf(segments, speeds, np.array(fr_out)/1000,
#              50, cmap="gist_earth_r")
# plt.xlabel("Radial Position / m")
# plt.ylabel("Wind Speed / ms$^-$$^1$")
# plt.colorbar(label="Rotational Nodal Force (kN/m)")
# plt.show()

# # Plot Normal Segment Force on contour
# plt.figure(1, figsize=(12, 6))
# plt.contourf(segments[-(len(segments)-1):], speeds, np.array(T_out)/1000,
#              50, cmap="gist_earth_r")
# plt.xlabel("Radial Position / m")
# plt.ylabel("Wind Speed / ms$^-$$^1$")
# plt.colorbar(label="Normal Segment Force (kN)")
# plt.show()

# # Plot Segmental Torque on contour
# plt.figure(1, figsize=(12, 6))
# plt.contourf(segments[-(len(segments)-1):], speeds, np.array(tau_out)/1000,
#              50, cmap="gist_earth_r")
# plt.xlabel("Radial Position / m")
# plt.ylabel("Wind Speed / ms$^-$$^1$")
# plt.colorbar(label="Segmental Torque (kNm)")
# plt.show()


""" Demonstration of Blade Shape """
# Plot the chord length against radial position
plt.figure(1, figsize=(12, 6))
plt.title("Blade Distribution", fontsize=20)
plt.plot(segments, chords, marker="o")
plt.plot(segments, np.array(thetas)/10, marker="o")
plt.xlabel("$r_i$, m", fontsize=15)
plt.ylabel(r"$c_i$, m; $\theta$$_i$/10$\degree$", fontsize=15)
plt.legend(["Chord Lengths", "Twist Angles"])
plt.show()


"""Plotting the profiles overlayed"""
# Initialise the figure for the overlay plot
plt.figure(1, figsize=(12, 12))
colour = iter(plt.cm.rainbow(np.linspace(0, 1, 17)))
for i in [42, 46, 4, 24, 12, 36, 26, 48, 13, 34, 33, 3, 11, 45, 15, 23, 38]:
    # Set the file number containing aerofoil data
    number = i

    # Force the number to be 0x for 0-9
    filenumb = f"{number:02d}"
    name = "Profile-" + filenumb + "-Geom.csv"

    # Store CSV data as pandas dataframe
    df = pd.read_csv(zf.open(name), header=None)
    df = df[pd.to_numeric(df[0], errors="coerce").notnull()]
    df = {0: pd.to_numeric(df[0]), 1: pd.to_numeric(df[1])}
    df = pd.DataFrame(df)

    c = next(colour)
    # Plot the blade profiles overlayed on eachother
    plt.plot(df[0], df[1], c=c)
    plt.xlim(-0.1, 1.1)
    plt.ylim(-0.6, 0.6)
    plt.title("Overlay Plot of Profiles", fontsize=30)
    plt.axhline(y=0, color="black", linestyle="--")

plt.show()
