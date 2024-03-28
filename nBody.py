###This .py produces a live plot of an nBody simulation with customisable initial positions, velocities and masses.###

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random
import math

###SETTINGS###
plotting = 'full' #'full' will plot entire trajectory, 'last' will only plot recent trajectory
live = True #Either plots live, or calculates total_steps timesteps and then plots that.
total_steps = 250
dimension = 3 #2 or 3, plots either two or three dimensions
arrangement = 'solar' #solar, random, three, testing
BH = False #Chucks a black hole at the solar system just for fun
solar_extraVel = [0, 0, 0.5] #Gives the solar system an extra velocity. (Au / yr)
N = 3 #Number of bodies in 'random' arrangement
rand_massRange = [1, 25] #Range of random bodies' mass (solar masses)
rand_posRange = [5, 5, 5]#Range of random bodies' positions in AU (+-x, +-y, +-z)
rand_velRange = [1, 1, 1]#Range of random bodies' velocities in AU / yr (+-x, +-y, +-z)

###To add:
#Live plot stop condition
#Stable orbit initial conditions
#earthTemp = True # Takes albedo = 0.3, Aabs/Arad = 0.25, e=1 T~254 * 1/D^2 in K

time_step = 0.01 #in years
time = 0 #keeps track of time
G = 4 * (math.pi**2) #au^3 sm^-1 yr^-2
max_force = 10 #Stops bodies from flying away, mainly to make it look nice.
bodies_list = [] #Prepares list of body objects



#Each body is an object of the class 'planet', with pos&vel as 3-vectors and mass.
class planet():
    def __init__(self, name, mass, pos, vel):
        self.mass = mass
        self.dotSize = linear_map(self.mass, 0, 20, 10, 75)
        self.pos = np.array(pos)
        self.vel = np.array(vel)
        self.pos_hist = []
        self.name = name
        
    #Updates position from changed velocity    
    def update_pos(self): 
        self.pos_hist.append([self.pos[0], self.pos[1], self.pos[2]])
        self.pos += (self.vel * time_step)

#Actually calculates how the bodies move:
def update_vels(body_list):
    #Loops through each body
    #Calculates force from all other bodies
    #Adds up total force
    #Alters body velocity from acceleration
    for current in body_list:
        force = np.array([0.0,0.0,0.0])
        
        for other in body_list:
            if other != current:

                try:
                    radius = np.linalg.norm(current.pos - other.pos)
                    r_hat = (other.pos - current.pos) / np.linalg.norm(other.pos - current.pos)
                
                    force_norm = (G * other.mass) / ( radius**2 )
                
                    force += (r_hat * force_norm * time_step)

                    if np.linalg.norm(force) > max_force:
                        force /= np.linalg.norm(force)
                        force *= max_force 

                except ZeroDivisionError:
                    pass #Only here in near impossible cases of bodies being in the same position.
                    
            
        acc = force
        current.vel += acc

#Tells each body to update position based on velocity and current position
def update_poss(body_list):
    for current in body_list:
        current.update_pos()

#Linear mapping for plotting bodies based on mass.
def linear_map(value, minIn, maxIn, minOut, maxOut):
    if value >= maxIn:
        return(maxOut)
    elif value <= minIn:
        return(minOut)
    else:
        spanIn = maxIn - minIn
        spanOut = maxOut - minOut

        #Finds 0-1 value along input span
        scale = (value - minIn) / spanIn

        #Changes this to output span value
        output = minOut + (scale * spanOut)
        return(output)

#Print info to terminal:
def printInfo(list):
    for bdy in list:
        print('Body:', bdy.name)
        print('Initial Position:', bdy.pos)
        print('Initial Velocity:', bdy.vel)
        print('=====')

#Prefills bodylist with rough solar system data. Black hole included for fun
if arrangement == 'solar':  
    bodies_list.append(planet('Sun', 1, [0.0, 0.0 ,0.0], [0.0, 0.0, 0.0]))
    #mercury
    bodies_list.append(planet('Mercury', 1.7e-7, [0.39, 0.0 ,0.0], [0.0, 10.0, 0.0]))
    #venus
    bodies_list.append(planet('Venus', 2.4e-6, [0.72, 0.0 ,0.0], [0.0, 7.4, 0.0]))
    #earth
    bodies_list.append(planet('Earth', 3.0e-6, [1, 0.0 ,0.0], [0.0, 6.3, 0.0]))
    #mars
    bodies_list.append(planet('Mars', 3.2e-7, [1.52, 0.0 ,0.0], [0.0, 5.1, 0.0]))
    # #jupiter
    # bodies_list.append(planet('Jupiter', 9.5e-4, [5.2, 0.0 ,0.0], [0.0, 2.8, 0.0]))
    # #saturn
    # bodies_list.append(planet('Saturn', 2.9e-4, [9.54, 0.0 ,0.0], [0.0, 2.0, 0.0]))
    # #uranus
    # bodies_list.append(planet('Uranus', 4.4e-5, [19.22, 0.0 ,0.0], [0.0, 1.4, 0.0]))
    # #neptune
    # bodies_list.append(planet('Neptune', 5.1e-5, [30.06, 0.0 ,0.0], [0.0, 1.1, 0.0]))
    # #BH
    if BH:
        bodies_list.append(planet('Black Hole', 100, [-25.0, -25.0, -40.0], [10.0, 10.0, 15.0]))

    for bdy in bodies_list:
        bdy.vel += solar_extraVel
    
#Fills bodylist with N bodies of random mass, position and velocity
elif arrangement == 'random':     
    for n in range(N):
        mass = random.uniform(rand_massRange[0], rand_massRange[1])
        pos_x = random.uniform(-rand_posRange[0],rand_posRange[0])
        pos_y = random.uniform(-rand_posRange[1],rand_posRange[1])
        pos_z = random.uniform(-rand_posRange[2],rand_posRange[2])
        vel_x = random.uniform(-rand_velRange[0],rand_velRange[0])
        vel_y = random.uniform(-rand_velRange[1],rand_velRange[1])
        vel_z = random.uniform(-rand_velRange[2],rand_velRange[2])
        if dimension == 2:
            pos_z = 0
            vel_z = 0
        bodies_list.append(planet(str(n), mass, [pos_x, pos_y, pos_z], [vel_x, vel_y, vel_z]))  

#Planet moon sun configuration
elif arrangement == 'three':
    
    t2 = 2*math.pi/3
    t3 = 2*t2
    v = 5
    bodies_list.append(planet('One', 1, [1.0, 0.0, 0.0], [0.0, v, 0.0]))
    bodies_list.append(planet('Two', 1, [math.cos(t2), math.sin(t2) ,0.0], [-v * math.sin(t2), v * math.cos(t2), 0.0]))
    bodies_list.append(planet('Three', 1, [math.cos(t3), math.sin(t3) ,0.0], [-v * math.sin(t3), v * math.cos(t3), 0.0]))

#Testing bodies:
else:
    bodies_list.append(planet('One', 1, [0.0, 0.0 ,0.0], [0.0, 0.9, 0.0]))
   
    bodies_list.append(planet('Two', 1, [2.0, -0.5 ,0.0], [0.0, 0.85, 0.0]))
    
    bodies_list.append(planet('Three',1, [4.0, .0 ,0.0], [0.0, 0.8, 0.0]))   


        
#PLOTTING:
#Live:
if live: 
    printInfo(bodies_list)

    #Prepares axis for 3d
    if dimension == 3:
        ax = plt.axes(projection = '3d')

    def animate(i):
        global time
        
        update_vels(bodies_list)
        update_poss(bodies_list)
        
        plt.cla()

        if dimension == 3:
                ax.set_title('Your N-Body Simulation! Time: ' +str(time)+' years.')
                ax.set_xlabel('x (AU)')
                ax.set_ylabel('y (AU)')
                ax.set_zlabel('z (AU)')

        for bdy in bodies_list:
            
            if plotting == 'full':
                x_live = [element[0] for element in bdy.pos_hist]
                y_live = [element[1] for element in bdy.pos_hist]
                z_live = [element[2] for element in bdy.pos_hist]
            elif plotting == 'last':
                x_live = [element[0] for element in bdy.pos_hist[-10:]]
                y_live = [element[1] for element in bdy.pos_hist[-10:]]
                z_live = [element[2] for element in bdy.pos_hist[-10:]]

            
            x_last = bdy.pos[0]
            y_last = bdy.pos[1]
            z_last = bdy.pos[2]


            if dimension == 3:
                ax.plot3D(x_live, y_live, z_live)
                ax.scatter3D(x_last, y_last, z_last, s = bdy.dotSize)
                #Name plotting:
                if arrangement == 'solar':
                    ax.text(x_last, y_last, z_last, bdy.name)

            elif dimension == 2:
                plt.plot(x_live, y_live)
                plt.title("Your N-Body Simulation! Time: " + str(time) + ' years.')
                plt.scatter(x_last, y_last, s = bdy.dotSize)
                
                #Name plotting:
                if arrangement == 'solar':
                    plt.text(x_last, y_last, bdy.name)
                    
        time = round(time + time_step, 2)
            
     
    ani = FuncAnimation(plt.gcf(), animate, interval = 1, frames = 100, repeat = True)
    plt.show()
            
#Static:
else:
    printInfo(bodies_list)
    #Prepares axis for 3d
    if dimension == 3:
        ax = plt.axes(projection = '3d')
        # ax2 = plt.axes()


    for dt in range(total_steps):
        update_vels(bodies_list)
        update_poss(bodies_list) 
    
    
    for bdy in bodies_list:
        x = [element[0] for element in bdy.pos_hist]
        y = [element[1] for element in bdy.pos_hist]
        z = [element[2] for element in bdy.pos_hist]
        
        x_final = bdy.pos[0]
        y_final = bdy.pos[1]
        z_final = bdy.pos[2]
    
        if dimension == 3:
            ax.plot3D(x, y, z)
            ax.scatter3D(x_final, y_final, z_final, s = bdy.dotSize)
        elif dimension == 2:
            plt.plot(x,y)
            plt.scatter(x_final , y_final)
    plt.show()
    plt.close()