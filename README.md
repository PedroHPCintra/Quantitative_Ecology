# Quantitative_Ecology :earth_americas: :monocle_face:

Latest update: 27/03/2023

Welcome! This repo is a storage for all of my codes related to quantative ecological systems. Until now, most of them are from classes that I took at the [Training Program in Quantitative Ecology 2023](https://www.ictp-saifr.org/qecoprogram/) by the [Serrapilheira Institute](https://serrapilheira.org/) and [ICTP-SAIFR](https://www.ictp-saifr.org/) in São Paulo, Brazil.

## Repo Structure :file_folder:

This repository is organized in the following way:

1. :file_folder: The first folders are related to the type of modelling approach, all codes inside the folder make use of that approach. For example, the **Differential_equations** folder contains only projects and codes that use either Ordinary Differential Equations or Partial Differential Equations to describe specific problems. Regardless of the specific model used (Lotka-Volterra, Metapopulations...).

2. :file_folder: Inside the main folders are each project. Each project has it's own folder too, containing the code (usually as a ```Jupyter Notebook``` in ```Python```), any additional files needed and other folders to store the plots or gifs from the simulations.

Overall the repository follows this structure:

:open_file_folder:```Model type``` $\rightarrow$ :open_file_folder:```Project folder``` $\rightarrow$ :computer: Codes + :open_file_folder: Plots + :paperclip: Additional files

## Usage

If you want to use any of the codes here make sure to pay attention to the **import section** of the code and check if you have all dependencies installed. Make sure to download the whole project folder as well, not only the code, it might have some additional files needed to run the code. If you have git:octocat: installed in your computer you can also clone the whole repository by typping

```git clone https://github.com/PedroHPCintra/Quantitative_Ecology.git```

Until now, the following projects are of my own authorship:

- :file_folder:```Competitive_exclusion_evolution```
- :file_folder:```Stochastic_model_Mimulus_guttatus```

Therefore I would like to be cited as **Cintra, P. H. P.** if you use any of them. If you want, the bibtex format for the citation is found below:
```
@software{cintra_2023,
  author        = "P. H. P. Cintra",
  address       = "Brazil",
  title         = "(Name of the project, for example Competitive Exclusion Evolution)",
  howpublished  = "Ver. 1",
  year          = "2023",
  url           = "Link to github page of the project, for example https://github.com/PedroHPCintra/Quantitative_Ecology/tree/main/Differential_equations/Competitive_exclusion_evolution"
}
```

## References and theoretical calculations

I'm also leaving this section to provide some links to theoretical calculations done by me or other papers related to the models and projects here. The theoretical work that is done by me (mostly for study) will be available at my [website](https://sites.google.com/view/pedrocintra).

- :file_folder:```Stochastic_model_Mimulus_guttatus```
1. Elderd, B. D., & Doak, D. F. (2006). Comparing the direct and community-mediated effects of disturbance on plant population dynamics: flooding, herbivory and Mimulus guttatus. _Journal of Ecology_, 656-669. URL: [https://www.jstor.org/stable/3879611](https://www.jstor.org/stable/3879611)
2. Lewontin, R. C., & Cohen, D. (1969). On population growth in a randomly varying environment. _Proceedings of the National Academy of sciences_, 62(4), 1056-1060. DOI: [https://doi.org/10.1073/pnas.62.4.1056](https://doi.org/10.1073/pnas.62.4.1056)

- :file_folder:```Metapopulations_corals```
1. McManus, L. C., Vasconcelos, V. V., Levin, S. A., Thompson, D. M., Kleypas, J. A., Castruccio, F. S., ... & Watson, J. R. (2020). Extreme temperature events will drive coral decline in the Coral Triangle. _Global Change Biology_, 26(4), 2120-2133. DOI: [https://doi.org/10.1111/gcb.14972](https://doi.org/10.1111/gcb.14972)
2. McManus, L. C., Forrest, D. L., Tekwa, E. W., Schindler, D. E., Colton, M. A., Webster, M. M., ... & Pinsky, M. L. (2021). Evolution and connectivity influence the persistence and recovery of coral reefs under climate change in the Caribbean, Southwest Pacific, and Coral Triangle. _Global change biology_, 27(18), 4307-4321. DOI: [https://doi.org/10.1111/gcb.15725](https://doi.org/10.1111/gcb.15725)
