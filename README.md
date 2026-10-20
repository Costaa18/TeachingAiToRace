# Teaching AI to Race

A small Python experiment that explores how an artificial intelligence can learn to drive around a 2D racing track.

The project combines [Pygame](https://www.pygame.org/) for the game simulation with [NEAT](https://neat-python.readthedocs.io/) (`neat-python`) for feed-forward neural networks. AI-controlled cars use distance sensors to detect the track borders and choose when to steer, accelerate, or reverse.

> **Project status:** This is an early prototype and learning project. The simulation and AI car control are implemented, while the full NEAT training/evolution loop is still a work in progress.

## Features

- 2D top-down racing track rendered with Pygame.
- AI cars controlled by feed-forward neural networks.
- Five distance sensors pointing in different directions:
  - `-90°`
  - `-45°`
  - `0°`
  - `45°`
  - `90°`
- Pixel-mask collision detection for the track borders and finish line.
- Checkpoints used to measure progress around the track.
- A configurable NEAT population in `config-feedforward.txt`.
- Visual sensor rays and a live count of cars that are still active.

## How the AI works

Each AI car receives five normalized sensor values. A sensor scans up to 150 pixels and returns the distance to the nearest track border.

The neural network has:

- **5 inputs:** one value per sensor.
- **4 outputs:** steer left, steer right, move forward, and move backward.
- **No hidden layers by default:** this is configured in `config-feedforward.txt`.

The car's fitness increases when it reaches checkpoints and when it completes the finish interaction. Cars are also removed from the simulation after colliding with the track border or remaining almost stationary for too long.

## Requirements

- Python 3.9 or newer
- Pygame
- neat-python

## Installation

Clone the repository and move into the project directory:

```bash
git clone https://github.com/Costaa18/TeachingAiToRace.git
cd TeachingAiToRace
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Windows:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install pygame neat-python
```

## Running the prototype

Run the application from the repository root so that the relative image paths can be resolved:

```bash
python main.py
```

A Pygame window will open with five AI cars on the track. The simulation ends when all cars are no longer active or when the window is closed.

## Human controls

The current default setup starts AI cars. The human-car control code is also available in `main.py` for experimentation:

| Key | Action |
| --- | --- |
| `W` | Accelerate |
| `S` | Reverse/brake |
| `A` | Turn left |
| `D` | Turn right |
| Close the window | Quit |

To use a human-controlled car, replace the initial AI car setup in `main.py` with a `PlayerCar` instance. The commented example near the game initialization shows the intended starting point.

## Project structure

```text
.
├── main.py                 # Game loop, cars, sensors, collisions, and AI control
├── utils.py                # Image scaling and car rotation helpers
├── config-feedforward.txt  # NEAT population and genome configuration
└── imgs/                   # Track, finish line, car, and background assets
```

## Configuration

The NEAT configuration can be adjusted in `config-feedforward.txt`. Useful settings include:

- `pop_size`: number of genomes in each generation.
- `num_inputs`: number of sensor inputs expected by each network.
- `num_outputs`: number of actions produced by each network.
- `num_hidden`: number of hidden nodes initially used.
- Mutation probabilities for weights, connections, and nodes.
- `max_stagnation` and `elitism`: how species and the best genomes are preserved.

If the number of sensors or actions changes in `main.py`, update `num_inputs` or `num_outputs` accordingly.

## Next steps

Possible improvements for continuing the experiment include:

- Connect the game evaluation to `population.run(...)`.
- Run one simulation per generation and assign each genome's fitness.
- Remove or reset cars between generations.
- Save and reload the best genome.
- Add a generation counter and training statistics.
- Tune the fitness function to reward faster, safer laps.
- Add a headless training mode so generations can run without rendering every frame.

## License

No license has been specified for this project yet.
