import os
import math
import copy
import queue
import scipy
import numpy
import random
import argparse
import warnings
import itertools

''' Computer-Aided Simulation Framework for Investigating Natural Selection and Species Extinction Dynamics '''


class Colony:

    def __init__(self, colony):
        # the colony's identification code
        self.colony = colony
        # the list data type to archive the colony's settlers
        self.settlers = list()
        # the dict data type to archive the colonies in the colony's neighborhood
        self.neighbors = set()

    def position(self, coordinate):
        # the colony's cartesian coordinates
        self.x, self.y = coordinate

    def colonization(self, clan, species):
        # inserting the colonizing (clan, species) among the settlers
        self.settlers.append((clan, species))


class Individual:

    def __init__(self,
                 code,
                 time,
                 clan,
                 colony,
                 parent,
                 species,
                 lifetime):
        # the individual's identification code
        self.code = code
        # the individual's birth time
        self.time = time
        # the individual's clan
        self.clan = clan
        # the individual's colony
        self.colony = colony
        # the individual's parent
        self.parent = parent
        # the individual's species
        self.species = species
        # the individual's lifetime
        self.lifetime = lifetime

    def death(self):
        # the individual's death time
        return self.time + self.lifetime

    def begetting(self, rate):
        return numpy.random.exponential(scale=1 / rate,
                                        size=None)


class Clan:

    def __init__(self,
                 clan,
                 species,
                 individuals,
                 colony,
                 births,
                 deaths):
        # the clan's identification code
        self.clan = clan
        # the clan's species
        self.species = species
        # the dict data type to archive the clan's individuals
        self.individuals = individuals
        # the list data type structure to archive the colonization history
        self.colonies = [colony]
        # the births counter
        self.births = births
        # the deaths counter
        self.deaths = deaths

    def birth(self,
              time,
              clan,
              colony,
              parent,
              species,
              lifetime):
        # updating the births counter
        self.births += 1
        # inserting the individual among the clan's individuals
        self.individuals[self.births] = Individual(self.births,
                                                   time,
                                                   clan,
                                                   colony,
                                                   parent,
                                                   species,
                                                   lifetime)
        return self.births

    def death(self, code):
        # updating the deaths counter
        self.deaths += 1
        # deleting the individual from the clan's individuals
        if code in self.individuals.keys():
            del self.individuals[code]

    def alliance(self, time, natives):
        # the dict data type structure to archive the pairs (previous identification code, current identification code)
        dictionary = dict()
        ex = copy.deepcopy(natives)
        for individual in ex.individuals.values():
            # updating the births counter
            self.births += 1
            # inserting the individual among the clan's individuals
            self.individuals[self.births] = Individual(self.births,
                                                       time,
                                                       self.clan,
                                                       self.colonies[-1],
                                                       None,
                                                       self.species,
                                                       time - individual.lifetime)
            # deleting the individual from the clan's individuals
            natives.death(individual.code)
            # inserting the pair (previous identification code, current identification code) into the dictionary
            dictionary[individual.code] = self.births
        return dictionary

    def migration(self, colony):
        # updating the clan's individuals colony for the migration departure
        for individual in self.individuals.values():
            individual.colony = None

    def colonization(self, colony):
        # updating the clan's individuals colony for the migration arrival
        for individual in self.individuals.values():
            individual.colony = colony
        # inserting the colony into the colonization history
        self.colonies.append(colony)

    def history(self):
        return self.births - self.deaths


def grid(districts):

    def distance(v, w):
        return math.sqrt(math.pow((v.x - w.x), 2) +
                         math.pow((v.y - w.y), 2))
    # structuring the colony register
    world = {colony: Colony(colony) for colony in range(districts)}

    def arange(N, K):
        return numpy.arange(start=0,
                            stop=math.pow(N, 1 / K))
    X, Y = arange(districts, 2), arange(districts, 2)
    # structuring the cartesian coordinates
    for colony, coordinate in zip(world.values(), [c for c in itertools.product(* [X, Y])]):
        colony.position(coordinate)
    # structuring the colonies in the neighborhood
    for colony in world.keys():
        for neighbor in world.keys():
            if colony != neighbor and distance(world[colony],
                                               world[neighbor]) < 1.5:
                world[colony].neighbors.add(neighbor)
                world[neighbor].neighbors.add(colony)
    return world


def lifespan(individual, alpha, improve):
    # the alpha lifetime
    alpha = numpy.random.uniform(low=individual.lifetime,
                                 high=individual.lifetime * (1 + alpha),
                                 size=None)
    # the beta lifetime
    beta = numpy.random.uniform(low=0,
                                high=individual.lifetime,
                                size=None)
    # randomly choosing the lifetime according to the improvement probability
    return numpy.random.choice([alpha, beta],
                               p=[improve, 1 - improve],
                               size=None)


def departure(time,
              code,
              clan,
              species,
              colony,
              rate,
              alpha,
              improve,
              nature,
              history,
              world,
              FES):
    # the migrant (clan, species)
    migrant = (clan, species)
    # randomly choosing the migration destination site among the neighbors of the origin site
    origin, site = colony, numpy.random.choice(
        [neighbor for neighbor in world[colony].neighbors])
    if migrant in world[origin].settlers:
        # removing the (clan, species) migrant among the settlers of the origin site
        world[origin].settlers.remove(migrant)
    # updating the clan individuals colony for the migration departure
    nature[clan].migration(origin)

    def migration(origin, site):
        # computing the cartesian distance between the origin site and the destination site
        x = (abs(world[origin].x - world[site].x) +
             abs(world[origin].y - world[site].y)) * 10000  # [1:10000] [km]
        # computing the average migration velocity of individuals, 5 [km/hours] into [km/years]
        v = 18250  # [km/years] -> 5 [km/h]
        return x / v
    # archiving the FES history
    story = copy.deepcopy(FES.queue)
    # initializing the FES
    FES = queue.PriorityQueue()
    # the inter-migration time
    x = migration(origin, site)
    # inserting the migration arrival event into the FES
    FES.put((time + x, (00,
                        clan,
                        species,
                        site,
                        'arrival')))
    # structuring the FES
    for element in story:
        (time, (code, clan, species, colony, event)) = element
        if (clan, species) != migrant:
            FES.put((time, (code,
                            clan,
                            species,
                            colony,
                            event)))
        else:
            if event in ['death']:
                FES.put((time, (code,
                                clan,
                                species,
                                colony,
                                event)))
    return FES


def freepath(N):
    # the radius of the human dimension
    d = 0.0015
    # the velocity of human running
    v = 54750  # [km/year] -> 15 [kmh/h]
    # the volume ot the battlefield
    volume = math.pow(10, 2) * d  # [1:10] [km]
    # the rate of collisions between individuals in the battlefield
    rate = (N / volume) * math.pi * math.pow(d, 2) * v
    return rate


def clash(time,
          code,
          clan,
          species,
          colony,
          rate,
          alpha,
          improve,
          nature,
          history,
          world,
          FES):
    # the battlefield colony
    battlefield = colony
    # the individual
    individual = nature[clan].individuals[code]
    # checking the war situation
    if len(world[battlefield].settlers) > 1:
        x = nature[clan].individuals[code]
        # searching the enemy faction
        if [enemy
            for (enemy, species) in world[battlefield].settlers
                if enemy != clan and nature[enemy].history() > 0]:
            faction = numpy.random.choice([enemy
                                           for (enemy, species) in world[battlefield].settlers
                                           if enemy != clan and nature[enemy].history() > 0])
        else:
            return FES
        y = numpy.random.choice([individual
                                 for individual in nature[faction].individuals.values()])
        individual = numpy.random.choice([x, y],
                                         p=[0.5, 0.5],
                                         size=None)
        breathless = x if individual != x else y
        FES = death(time,
                    breathless.code,
                    breathless.clan,
                    breathless.species,
                    breathless.colony,
                    rate,
                    alpha,
                    improve,
                    nature,
                    history,
                    world,
                    FES)
        # checking the war situation
        if len(world[battlefield].settlers) > 1:
            N = sum([nature[enemy].history() for (enemy, species)
                    in world[battlefield].settlers if enemy != clan])
            rate = freepath(N)
            if rate > 0:
                x = numpy.random.exponential(scale=1 / rate,
                                             size=None)
                if time + x < individual.death():
                    # inserting the next clash event into the FES
                    FES.put((time + x, (individual.code,
                                        individual.clan,
                                        individual.species,
                                        battlefield,
                                        'clash')))
    # checking the war situation
    if len(world[battlefield].settlers) < 2:
        # archiving the FES history
        story = copy.deepcopy(FES.queue)
        # initializing the FES
        FES = queue.PriorityQueue()
        # structuring the FES
        for element in story:
            (time, (code, clan, species, colony, event)) = element
            if (clan, species) not in world[battlefield].settlers:
                FES.put((time, (code,
                                clan,
                                species,
                                colony,
                                event)))
            else:
                if event in ['death']:
                    FES.put((time, (code,
                                    clan,
                                    species,
                                    colony,
                                    event)))
        # colonizing the battlefield
        FES = colonization(time,
                           individual.code,
                           individual.clan,
                           individual.species,
                           individual.colony,
                           rate,
                           alpha,
                           improve,
                           nature,
                           history,
                           world,
                           FES)
    return FES


def war(time,
        code,
        clan,
        species,
        colony,
        rate,
        alpha,
        improve,
        nature,
        history,
        world,
        FES):
    # the battlefield colony
    battlefield = colony
    # the war time
    war = time
    # archiving the FES history
    story = copy.deepcopy(FES.queue)
    # initializing the FES
    FES = queue.PriorityQueue()
    # structuring the FES
    for element in story:
        (time, (code, clan, species, colony, event)) = element
        if (clan, species) not in world[battlefield].settlers:
            FES.put((time, (code,
                            clan,
                            species,
                            colony,
                            event)))
        else:
            if event in ['death']:
                FES.put((time, (code,
                                clan,
                                species,
                                colony,
                                event)))
    # for each faction (clan, species) in war
    for (clan, species) in world[battlefield].settlers:
        N = sum([nature[enemy].history() for (enemy, species)
                in world[battlefield].settlers if enemy != clan])
        for individual in nature[clan].individuals.values():
            rate = freepath(N)
            if rate > 0:
                x = numpy.random.exponential(scale=1 / rate,
                                             size=None)
                if war + x < individual.death():
                    # inserting the next clash event into the FES
                    FES.put((war + x, (individual.code,
                                       individual.clan,
                                       individual.species,
                                       battlefield,
                                       'clash')))
    return FES


def alliance(time,
             foreign,
             native,
             colony,
             nature,
             world,
             FES):
    # the species capable of allying
    species = 'sapiens'
    # the pairs (previous identification code, current identification code)
    dictionary = nature[foreign].alliance(time, nature[native])
    # checking for extinction
    if nature[native].history() < 1:
        # deleting the (clan, species) from the current colony in case of extinction
        if (native, species) in world[colony].settlers:
            world[colony].settlers.remove((native, species))
    # archiving the FES history
    story = copy.deepcopy(FES.queue)
    # initializing the FES
    FES = queue.PriorityQueue()
    # structuring the FES
    for element in story:
        (time, (code, clan, species, colony, event)) = element
        if (clan, species) not in [(native, 'sapiens')]:
            FES.put((time, (code,
                            clan,
                            species,
                            colony,
                            event)))
        else:
            if event in ['death']:
                FES.put((time, (dictionary[code],
                                foreign,
                                species,
                                colony,
                                event)))
    return FES


def colonization(time,
                 code,
                 clan,
                 species,
                 colony,
                 rate,
                 alpha,
                 improve,
                 nature,
                 history,
                 world,
                 FES):
    # randomly choosing the next migration time
    m = numpy.random.uniform(low=0,
                             high=5,
                             size=None)
    # inserting the next birth by the individual into the FES
    for individual in nature[clan].individuals.values():
        if individual.death() - time > 0:
            x = individual.begetting(rate + 0.85)
            if time + x < individual.death():
                FES.put((time + x, (individual.code,
                                    individual.clan,
                                    individual.species,
                                    individual.colony,
                                    'birth')))
    # inserting the next clan migration into the FES
    FES.put((time + m, (00,
                        clan,
                        species,
                        colony,
                        'departure')))
    return FES


def arrival(time,
            code,
            clan,
            species,
            colony,
            rate,
            alpha,
            improve,
            nature,
            history,
            world,
            FES):
    # the migrant (clan, species)
    migrant = (clan, species)
    # the origin site and the destination site
    origin, site = nature[clan].colonies[-1], colony
    # calling the colonization functions
    nature[clan].colonization(site)
    world[site].colonization(clan, species)
    # checking for other settlers into the colony
    if len(world[site].settlers) > 1:
        if species in ['sapiens']:
            # archiving the foreign clan
            foreign = clan
            # the list data type to archive the natives
            natives = [clan
                       for (clan, species) in world[site].settlers
                       if clan != foreign]
            for native in natives:
                if nature[native].species in ['sapiens']:
                    FES = alliance(time,
                                   foreign,
                                   native,
                                   site,
                                   nature,
                                   world,
                                   FES)
        # checking for other settlers into the colony
        if len(world[site].settlers) > 1:
            FES = war(time,
                      code,
                      clan,
                      species,
                      colony,
                      rate,
                      alpha,
                      improve,
                      nature,
                      history,
                      world,
                      FES)
        # colonizing the site
        else:
            FES = colonization(time,
                               code,
                               clan,
                               species,
                               colony,
                               rate,
                               alpha,
                               improve,
                               nature,
                               history,
                               world,
                               FES)
    # colonizing the site
    else:
        FES = colonization(time,
                           code,
                           clan,
                           species,
                           colony,
                           rate,
                           alpha,
                           improve,
                           nature,
                           history,
                           world,
                           FES)
    # updating the history on the counts
    history[species][time] = sum(nature[clan].history(
    ) for clan in nature.keys() if not nature[clan].species != species)
    return FES


def birth(time,
          code,
          clan,
          species,
          colony,
          rate,
          alpha,
          improve,
          nature,
          history,
          world,
          FES):
    # the parent individual
    individual = nature[clan].individuals[code]
    # inserting the birth in the clan register and returning the identification code of the child individual
    code = nature[clan].birth(time,
                              individual.clan,
                              individual.colony,
                              individual,
                              individual.species,
                              lifespan(individual,
                                       alpha,
                                       improve))
    # inserting the next birth by the parent individual into the FES
    if individual.death() - time > 0:
        x = individual.begetting(rate)
        if time + x < individual.death():
            FES.put((time + x, (individual.code,
                                individual.clan,
                                individual.species,
                                individual.colony,
                                'birth')))
    # the child individual
    individual = nature[clan].individuals[code]
    # inserting the death of the child individual into the FES
    FES.put((individual.death(), (individual.code,
                                  individual.clan,
                                  individual.species,
                                  individual.colony,
                                  'death')))
    # inserting the next birth by the child individual into the FES
    if individual.death() - time > 0:
        x = individual.begetting(rate)
        if time + x < individual.death():
            FES.put((time + x, (individual.code,
                                individual.clan,
                                individual.species,
                                individual.colony,
                                'birth')))
    # updating the history on the counts
    history[species][time] = sum(nature[clan].history(
    ) for clan in nature.keys() if not nature[clan].species != species)


def death(time,
          code,
          clan,
          species,
          colony,
          rate,
          alpha,
          improve,
          nature,
          history,
          world,
          FES):
    # the death (clan, species)
    death = (code, clan)
    # deleting the individual from the clan individuals
    nature[clan].death(code)
    if nature[clan].history() < 1:
        # deleting the (clan, species) from the current colony in case of extinction
        if (clan, species) in world[colony].settlers:
            world[colony].settlers.remove((clan, species))
    # updating the history on the counts
    history[species][time] = sum(nature[clan].history(
    ) for clan in nature.keys() if not nature[clan].species != species)
    # archiving the FES history
    story = copy.deepcopy(FES.queue)
    # initializing the FES
    FES = queue.PriorityQueue()
    for element in story:
        (time, (code, clan, species, colony, event)) = element
        if (code, clan) != death:
            FES.put((time, (code,
                            clan,
                            species,
                            colony,
                            event)))
    return FES
