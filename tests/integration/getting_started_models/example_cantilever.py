from framat import Model                  # Import the FramAT model object

model = Model.from_example('cantilever')  # Load the cantilever example model
model.run()                               # Run the pre-defined analysis
