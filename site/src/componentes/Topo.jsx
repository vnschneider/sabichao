import { GithubLogo } from "@phosphor-icons/react";
import { REPOSITORIO } from "../conteudo.js";
import "./Topo.css";

export default function Topo() {
  return (
    <header className="topo">
      <div className="largura topo-linha">
        <a className="marca" href="#">
          <img src="/favicon.svg" alt="" width="28" height="25" />
          Sabichao
        </a>
        <nav aria-label="Secoes">
          <a href="#recursos">Recursos</a>
          <a href="#como">Como funciona</a>
          <a href="#seguranca">Seguranca</a>
          <a href="#perguntas">Perguntas</a>
          <a className="topo-github" href={REPOSITORIO} aria-label="Codigo-fonte no GitHub">
            <GithubLogo size={20} weight="fill" />
          </a>
        </nav>
      </div>
    </header>
  );
}
