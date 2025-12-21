# Installatie van de uFactory-template




Voor dat je begint dien je een clone van de `my_ufactory_ROS2` repository te maken.


## Cloning de ROS2 Universal Robots template
Voor het maken van de ROS2 Universal Robots template maak je gebruik van een Github clone die is voorbereid. Je kunt er voor kiezen om deze clone onder een eigen account van Github te plaatsen (1e keuze hieronder). Je kunt daarna eenvoudig backup's van je werk maken naar je eigen Github account.

> we maken gebruik van een prefix my_uf in de packages van de repository om onderscheid te maken met de standaard Universal Robots packages.

:::::{card} 

::::{tab-set}

:::{tab-item} Met GIT-repository support

* Maak een account aan bij [Github](https://github.com/) en login op dit account

* Open de [my_uf_ROS2](https://github.com/AvansMechatronica/my_ufactory_ROS2) repository

* Maak een Fork van de repository naar je eigen Github account door op het **Fork icoon**  te klikken:

![image](../images/fork.jpg)

* Volg de instructies, maar wijzig de naam van de nieuwe repository niet. Bevestig met **Create Fork**  

* Nu kun je de workspace als volgt creëren

```bash
mkdir -p ~/my_uf_ws/src
cd ~/my_uf_ws/src
git clone https://github.com/<jouw_account_naam>/my_ufactory_ROS2.git
```

*ps. Het gebruik van github (zoals add, commit & push commando's) valt  buiten de scope van deze documentatie*

:::

:::{tab-item} Zonder GIT-repository support

* Je kunt de workspace als volgt creëren
```bash
mkdir -p ~/my_uf_ws/src
cd ~/my_uf_ws/src
git clone https://github.com/AvansMechatronica/my_uf_ROS2.git
```

:::

::::

:::::



## Installatie van Universal Robot support packages

```bash
cd ~/my_uf_ws/src/my_uf_ROS2/install
./install
```

## Bouwen van de workspace
> Dit is al gebeurd in de installatie. Wijzig je iets in de workspace dan kun je als volgt bouwen
```bash
# Build the workspace
cd ~/my_uf_ws
colcon build --symlink-install
source install/setup.bash

```