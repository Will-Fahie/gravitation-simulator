import math
import sys
import pygame


pygame.init()
clock = pygame.time.Clock()

screen_width = screen_height = 750
screen = pygame.display.set_mode([750, 750])
pygame.display.set_caption("Will's orbital modeller")

centre_x = screen_width // 2
centre_y = screen_height // 2


# gravitational constant
G = 6.67 * 10 ** -11

# astronomical Unit
AU = 1.50 * 10 ** 11
distance_scale = 200 / AU

day = 60 * 60 * 24  # one day in seconds
time_step = day  # each step is one day


instantiated = False
freq_changing = False
final_freq = 0


class Body(object):
    """A class representing an astronomical body"""

    def __init__(self, name, mass, vel_x, vel_y, pos_x, pos_y, colour, diameter):
        self.name = name
        self.mass = mass  # mass of body in kg
        self.vel_x = vel_x  # horizontal velocity in m/s
        self.vel_y = vel_y  # vertical velocity in m/s
        self.pos_x = pos_x  # horizontal position in m
        self.pos_y = pos_y  # vertical position in m
        self.colour = colour
        self.diameter = diameter
        self.radius = diameter // 2
        # draw lines method needs to points in positions list
        self.positions = [(self.pos_x * distance_scale + centre_x, self.pos_y * distance_scale + centre_y),
                          (self.pos_x * distance_scale + centre_x, self.pos_y * distance_scale + centre_y)]

    def calc_grav_force(self, other_body):
        """Calculates gravitational force acting on this body from another body"""

        # calculates distance
        dx = other_body.pos_x - self.pos_x
        dy = other_body.pos_y - self.pos_y
        d = math.sqrt(dx ** 2 + dy ** 2)

        # calculates resultant force
        f = G * self.mass * other_body.mass / (d ** 2)

        # resolves force into x and y components
        theta = math.atan2(dy, dx)  # unlike atan, atan2 considers signs
        f_x = f * math.cos(theta)
        f_y = f * math.sin(theta)

        return f_x, f_y

    def draw(self):
        pygame.draw.circle(screen,
                           self.colour,
                           (self.pos_x * distance_scale + centre_x, self.pos_y * distance_scale + centre_y),
                           self.radius)


def print_info(bodies):
    """Prints each body's position and velocity"""
    for body in bodies:
        print(f"""
        {body.name}   
        Position = x: {body.pos_x} y: {body.pos_y}   
        Velocity = y: {body.vel_x} x: {body.vel_y}\n""")
    print()


def calc_total_force(bodies):
    """Calculates the net force acting on each body"""
    forces = {}

    for body in bodies:
        total_f_x = 0
        total_f_y = 0
        for other in bodies:
            if other is body:
                continue  # doesn't calculate force from body on itself
            f_x, f_y = body.calc_grav_force(other)
            total_f_x += f_x
            total_f_y += f_y

        forces[body] = (total_f_x, total_f_y)

    return forces


def update_velocities_positions(bodies, forces, trail=False):
    """Updates the velocity and position of each body based on the net force acting on it"""
    for body in bodies:
        f_x, f_y = forces[body]

        # updates velocities
        body.vel_x += f_x / body.mass * time_step
        body.vel_y += f_y / body.mass * time_step

        # updates positions
        body.pos_x += body.vel_x * time_step
        body.pos_y += body.vel_y * time_step

        # adds new position to positions list
        if trail:
            body.positions.append((body.pos_x * distance_scale + centre_x, body.pos_y * distance_scale + centre_y))
            if len(body.positions) == 75:
                body.positions.pop(0)


def get_choice():
    """Prints model options, gets choice from user, and runs the according model function"""
    options = {"1:": "Solar system",
               "2:": "Two suns",
               "3:": "Earth and sun",
               "4:": "Earth and moving sun",
               "5:": "Exit"}

    # prints options
    print()
    for k, v in options.items():
        print(k, v)

    # loops until valid options given
    while True:
        try:
            usr_choice = int(input("\nSelect model: "))
            if usr_choice == 5:
                sys.exit()
            else:
                draw_trail = input("Draw trail? (y/n): ")
                if draw_trail.upper() == "Y":
                    return usr_choice, True
                elif draw_trail.upper() == "N":
                    return usr_choice, False
                else:
                    raise ValueError
        except ValueError:
            print("Not valid")


def draw(bodies, start, trail):
    """Updates forces, positions and velocities and draws bodies on screen, and trail if trail is True"""
    screen.fill((0, 0, 0))

    if start:
        forces = calc_total_force(bodies)
        update_velocities_positions(bodies, forces, trail)

    for body in bodies:
        body.draw()
        if trail:
            pygame.draw.lines(screen, body.colour, False, body.positions, body.diameter // 4)


def change_frequency():
    """Used to gradually increase time_step (and thus period of orbit) up to a resonant frequency"""
    global time_step, freq_changing, final_freq
    difference = abs(final_freq - time_step)

    if difference > 100000:
        if time_step < final_freq:
            time_step += 25000
        elif time_step > final_freq:
            time_step -= 25000
    else:
        time_step = final_freq
        freq_changing = False


def main():
    """Main function (bottom of stack)"""
    global instantiated, time_step, freq_changing, final_freq

    start = False
    usr_choice, trail = get_choice()

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Pauses/resumes simulation
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start is False:
                    start = True
                else:
                    start = False

        key = pygame.key.get_pressed()
        if key[pygame.K_RIGHT]:
            time_step += day // 4  # accelerates time by 1/4 day
        if key[pygame.K_LEFT]:
            time_step -= day // 4  # decelerates time by 1/4 day
        if key[pygame.K_UP]:
            time_step += day // 8  # accelerates time by 1/8 day
            print(time_step)
        if key[pygame.K_DOWN]:
            time_step -= day // 8  # decelerates time by 1/8 day
            print(time_step)

        if freq_changing:
            # allows for a gradual increase in frequency until the desired frequency is met, without "breaking" paths
            change_frequency()

        # resonant frequencies
        if key[pygame.K_0]:
            freq_changing = True
            final_freq = 0
        if key[pygame.K_1]:
            freq_changing = True
            final_freq = 4946400
        if key[pygame.K_2]:
            freq_changing = True
            final_freq = 6048000
        if key[pygame.K_3]:
            freq_changing = True
            final_freq = 7844400
        if key[pygame.K_4]:
            freq_changing = True
            final_freq = 9248400
        if key[pygame.K_5]:
            freq_changing = True
            final_freq = 11296800

        if not instantiated:
            if usr_choice == 1:
                """The sun and first 4 planets of our solar system"""

                sun = Body("Sun", 1.99 * 10 ** 30, 0, 0, 0, 0, (252, 207, 3), 40)
                mercury = Body("Mercury", 3.29 * 10 ** 23, 0, 47.4 * 1000, 0.39 * AU, 0, (213, 210, 209), 6)
                venus = Body("Venus", 4.87 * 10 ** 24, 0, 34.8 * 1000, 0.72 * AU, 0, (139, 125, 130), 15)
                earth = Body("Earth", 5.97 * 10 ** 24, 0, 29.8 * 1000, 1 * AU, 0, (27, 164, 209), 16)
                mars = Body("Mars", 6.39 * 10 ** 23, 0, 24.1 * 1000, 1.52 * AU, 0, (156, 46, 53), 10)
                bodies = [sun, mercury, venus, earth, mars]

            if usr_choice == 2:
                """Two suns both moving at 7.5 km/s but in opposite directions, with a distance of 2 AU between the two 
                *undisturbed* parallel paths"""

                sun_1 = Body("Sun", 1.99 * 10 ** 30, 0, 7.5 * 1000, -1 * AU, -1 * AU, (252, 207, 3), 40)
                sun_2 = Body("Sun", 1.99 * 10 ** 30, 0, -7.5 * 1000, 1 * AU, 1 * AU, (252, 207, 3), 40)
                bodies = [sun_1, sun_2]

            if usr_choice == 3:
                """Earth orbiting the sun, where sun is stationary relative to observer"""

                sun = Body("Sun", 1.99 * 10 ** 30, 0, 0, 0, 0, (252, 207, 3), 40)
                earth = Body("Earth", 5.97 * 10 ** 24, 0, 29.8 * 1000, 1 * AU, 0, (27, 164, 209), 16)
                bodies = [sun, earth]

            if usr_choice == 4:
                """Earth orbiting the sun, but sun is moving relative to observer"""

                sun = Body("Sun", 1.99 * 10 ** 30, 5 * 1000, 0, -1 * AU, 0, (252, 207, 3), 40)
                earth = Body("Earth", 5.97 * 10 ** 24, 0, 29.8 * 1000, 0, 0, (27, 164, 209), 16)
                bodies = [sun, earth]

            instantiated = True  # Prevents bodies from being recreated

        draw(bodies, start, trail)
        pygame.display.update()


if __name__ == "__main__":
    main()
