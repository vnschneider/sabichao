import Topo from "./componentes/Topo.jsx";
import Heroi from "./componentes/Heroi.jsx";
import Recursos from "./componentes/Recursos.jsx";
import Passos from "./componentes/Passos.jsx";
import Apps from "./componentes/Apps.jsx";
import Garantias from "./componentes/Garantias.jsx";
import Perguntas from "./componentes/Perguntas.jsx";
import Rodape from "./componentes/Rodape.jsx";

export default function App() {
  return (
    <>
      <Topo />
      <main>
        <Heroi />
        <Recursos />
        <Passos />
        <Apps />
        <Garantias />
        <Perguntas />
      </main>
      <Rodape />
    </>
  );
}
