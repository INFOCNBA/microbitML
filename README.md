# microbitML


Framework and proof of concept for Machine Learning practices (perceptrons, MLP and so on) using a swarm of version2 [BBC Micro:bit](https://python.microbit.org/)'s, for high-school formal Education.

Microbits communicate via bluetooth, but are grouped (in app layer) in teams. Within each team, each MB must  assume a different role.  The whole class uses the same channel, in order to accommodate a monitoring/teaching node.


## Proof of concept


In the case of this proof of concept, a Perceptron is formed by a team of three MB. Two acting as inputs/dendrites and one as the output/axon. Not a multi-layer perceptron, all three Microbits compose one perceptron. These are the roles of each one:

- Role A: sends a count of 3 things, multiplied by 1, valid values: {0,1,2,3}.
- Role B: sends a count of (other) 3 things, multiplied by 2, valid values: {0,2,4,6}
- Role Z: Receives the data from A and B, adds them and applies a binary activation function that will be "True" iif the sum exceeds 6.


![](README.d/neuronaMB.png)

Count on input nodes are updated by pressing buttons A and B. Here's a detail on Role Z's output:

![](README.d/z_binary_output.png)


## Usage:  proof-of-concept 

1. Download the same .hex file to every Microbit in class (teaching node is not implemented yet)
2. Separate the class in groups of three MB's. Maybe groups of six~ten students, sharing 3 MB, is fine.
3. Each group must have all MB's configured accordingly to assigned group and role. To change those, keep pin one  connected to ground, and press buttons A and B. When done, disconnect pin 1, to restore normal button operation.
   1. Button A cycles role. In the p-o-c, available roles are {A,B,Z}
   2. Button B cycles group {0,1,..,9}
      ![](README.d/config_role_group.png)      
      
1. At any time,  group and role, can be checked by touching the Micro:bit logo. Avoid group 0, since any node can fallback to that group if eventually restarted.
2. Your class is set
3. You can now conduct any teaching experience you want. For example:
   1. Give the class some context on Microbits A and B being inputs for a perceptron, and vertical bar in Z is the boolean output (giving them a printed sheet with the neuron sketch above to place them, might help). When ready, a task for them would be to figure out the answer to questions like:
	   1. Guess what TWO math operation drives vertical bar in Z? (answer: sums A and B, then compares to 6)
	   2. What's the difference between A and B? ( A multiplies it's count by 1, B multiplies it's count by 2)
   2. After all groups inferred the answer to your questions, just by discussing individual  interaction with their MB, you can discuss with them in Machine Learning jargon:
      1. Microbits A,B and Z form a **perceptron**, the basic processing element in ML
      2. A and B store different **weights**, that constitute a **ML Model**
      3. Z sums and applies an **activation function**. It's output might be a final **classification** of the model. Or, if part of a different **architecture**, the output might  **feed forward**  yet another **layer** of perceptrons in an **MLP**. Z might apply a **bias**, with is also part of the *ML model* . 
      4. *weights* of A and B are fixed here, but the "Learning" part of "Supervised ML" consists of adapting those *weights and bias*, by means of several thousands of cycles of exposure to  **tagged samples**, that form a **dataset**. Each cycle emprobes the model by applying small changes in *weights and bias*. That's called **training**. Training goes on, until some metric is considered satisfactory by the **data scientists** that designed the **ML pipeline**.
      5. As part of the *ML pipeline* the *model* is **validated** against an all-new *dataset*. If that metrics holds the model is considered production-grade. Otherwise, more *training* is needed. The huge  amount the training data needed, is often the main weakness of *ML pipelines* and the resulting *Supervised Machine Learning models*
      6. Conclusion: when consuming ML-equipped devices, ALWAYS beware that errors in classification will happen, specially if the underlying *model* is not *trained* for your particular application.


![](README.d/practica_241029.png)
## Credits

- heavily based on Prof Fujio Yamamoto's blog article on [building a Microbit network emulating a MLP](https://sparse-dense.blogspot.com/2018/06/microbittwo-layer-perceptronxor.html). Thanks a bunch, Mr Yamamoto!!
- (C) 2024 - [Leandro Batlle](https://www.linkedin.com/in/lean-b/) - Área de Innovación Educativa Científico-Tecnológica - [Colegio Nacional de Bs As](https://www.cnba.uba.ar)

