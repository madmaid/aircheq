import * as React from "react";
import * as moment from "moment";
import styled from "styled-components";

import { DetailLink } from "./ProgramDetail";
import { ProgList, ProgContainer, ProgChannel, ProgTime } from "./ProgramList";
import * as model from "../stores/program";

const ReservedTitle = styled(DetailLink)`
  display: block;
`;

const ReservedProgram = (props: { program: model.IProgram; key: number }) => {
  const { program, key } = props;

  const start = program.start.locale("ja");
  const toStart = moment.duration(start.diff(moment())).locale("ja");
  return (
    <ProgContainer key={key}>
      <ProgChannel>{program.channelJP}</ProgChannel>
      <ProgTime>{start.format("MM/DD(ddd) HH:mm")}</ProgTime>
      <ReservedTitle to={"/program/" + program.id.toString()}>
        {program.title}
      </ReservedTitle>
      <div>{toStart.humanize()}後</div>
    </ProgContainer>
  );
};

type State = {
  programs: model.IProgram[];
  intervalId?: number;
};

class Reserved extends React.Component<{}, State> {
  state: State;
  constructor() {
    super({});
    this.state = {
      programs: []
    };
  }
  componentDidMount() {
    model.fetchReserved().then(programs => {
      this.setState({ programs: programs });
    });
    const intervalId = setInterval(() => {
      model.fetchReserved().then(programs => {
        this.setState({ programs: programs });
      });
    }, 10000);
    this.setState({ intervalId: intervalId });
  }
  componentWillUnmount() {
    if (this.state.intervalId !== undefined) {
      clearInterval(this.state.intervalId);
    }
  }
  render() {
    return (
      <ProgList>
        {(() =>
          this.state.programs
            .sort((i, j) => {
              if (i.start.isBefore(j.start)) {
                return -1;
              } else if (i.start.isAfter(j.start)) {
                return 1;
              } else {
                return 0;
              }
            })
            .map((p: model.IProgram, i: number) => (
              <ReservedProgram program={p} key={i} />
            )))()}
      </ProgList>
    );
  }
}

export default Reserved;
