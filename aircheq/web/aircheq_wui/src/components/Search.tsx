import React from "react";
import * as Modal from "react-modal";
import { match as Match, Link, Redirect } from "react-router-dom";
import styled from "styled-components";

import "whatwg-fetch";

import {
  ProgList,
  ProgContainer,
  ProgService,
  ProgChannel,
  ProgTime,
  ProgDuration,
  ProgReserved
} from "./ProgramList";
import { DetailLink } from "./ProgramDetail";
import { Input, InputForm, SendButton } from "./FormUtil";

import { Program, jsonToProgram } from "../stores/program";

type Query = {
  id: string;
  service: string;
  channel: string;
  title: string;
  info: string;
};

type State = Query & {
  result: Program[];
};

class SearchForm extends React.Component<{}, State> {
  state: State;
  constructor() {
    super({});
    this.state = {
      id: "",
      service: "",
      channel: "",
      title: "",
      info: "",
      result: []
    };
  }
  render() {
    return (
      <div>
        <InputForm>
          <Input
            placeholder="id"
            type="text"
            value={this.state.id}
            onChange={e => {
              this.setState({ id: e.currentTarget.value });
            }}
            onKeyPress={this.onKeyPress}
          />
          <Input
            placeholder="service"
            type="text"
            value={this.state.service}
            onChange={e => {
              this.setState({ service: e.currentTarget.value });
            }}
            onKeyPress={this.onKeyPress}
          />
          <Input
            placeholder="channel"
            type="text"
            value={this.state.channel}
            onChange={e => {
              this.setState({ channel: e.currentTarget.value });
            }}
            onKeyPress={this.onKeyPress}
          />
          <Input
            placeholder="title"
            type="text"
            value={this.state.title}
            onChange={e => {
              this.setState({ title: e.currentTarget.value });
            }}
            onKeyPress={this.onKeyPress}
          />
          <Input
            placeholder="info"
            type="text"
            value={this.state.info}
            onChange={e => {
              this.setState({ info: e.currentTarget.value });
            }}
            onKeyPress={this.onKeyPress}
          />
          <SendButton
            onClick={(e: any) => {
              e.preventDefault();
              this.search();
            }}
          >
            検索
          </SendButton>
        </InputForm>
        <SearchResult result={this.state.result} />
      </div>
    );
  }
  genQuery(): Query {
    const valid = /\s+/g;
    return {
      id: this.state.id.replace(valid, ""),
      service: this.state.service.replace(valid, ""),
      channel: this.state.channel.replace(valid, ""),
      title: this.state.title.replace(valid, ""),
      info: this.state.info.replace(valid, "")
    };
  }
  search() {
    const query: Query = this.genQuery();

    const isAllEmpty = Object.keys(query)
      .map(k => query[k])
      .every(v => v === "");
    if (isAllEmpty) return;

    fetch("/api/search.json", {
      method: "POST",
      body: JSON.stringify(query),
      headers: {
        "Content-Type": "application/json"
      }
    })
      .then(res => res.json())
      .then(json => {
        this.setState({ result: json.map((p: any) => jsonToProgram(p)) });
      });
  }
  onKeyPress = (event: any) => {
    if (event.key === "enter") {
      this.search();
    }
  };
}

type Props = {
  result: Program[];
};

const SearchResult = (props: Props) => (
  <ProgContainer>
    {(() =>
      props.result.map((program: Program, i: number) => (
        <ProgContainer key={i}>
          <ProgReserved>{program.isReserved ? "予約済" : ""}</ProgReserved>
          <ProgChannel>{program.channelJP}</ProgChannel>
          <DetailLink to={"/program/" + program.id.toString()}>
            {program.title}
          </DetailLink>

          <ProgTime>{program.start.locale("ja").format("LLLL")}</ProgTime>
          <ProgTime>{program.end.locale("ja").format("LLLL")}</ProgTime>
          <ProgDuration>
            {program.duration.locale("ja").asMinutes()}分間
          </ProgDuration>
        </ProgContainer>
      )))()}
  </ProgContainer>
);

export { SearchForm as default };
