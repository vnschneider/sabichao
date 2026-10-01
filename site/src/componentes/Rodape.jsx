import { REPOSITORIO } from "../conteudo.js";
import "./Rodape.css";

export default function Rodape() {
  return (
    <footer className="rodape">
      <div className="largura rodape-linha">
        <p>Sabichao e uma ferramenta independente e nao oficial, sem vinculo com o IFMA ou com o SUAP.</p>
        <p className="rodape-links">
          <a href={REPOSITORIO}>Codigo-fonte</a>
          <a href={`${REPOSITORIO}/blob/main/LICENSE`}>Licenca AGPL-3.0</a>
        </p>
      </div>
    </footer>
  );
}
