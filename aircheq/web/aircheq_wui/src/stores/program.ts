import * as moment from "moment";
import "whatwg-fetch";

interface IProgram {
  id: number;
  service: string;
  channel: string;
  channelJP: string;
  title: string;
  info: string;
  start: moment.Moment;
  end: moment.Moment;
  duration: moment.Duration;

  isMovie: boolean;
  isRepeat: boolean;
  isReserved: boolean;
  isRecorded: boolean;
}

class Program implements IProgram {
  constructor(
    readonly id: number,
    readonly service: string,
    readonly channel: string,
    readonly channelJP: string,
    readonly title: string,
    readonly info: string,
    readonly start: moment.Moment,
    readonly end: moment.Moment,
    readonly duration: moment.Duration,

    readonly isMovie: boolean,
    readonly isRepeat: boolean,
    readonly isReserved: boolean,
    readonly isRecorded: boolean
  ) {}
}

function jsonToProgram(json: any) {
  const start = moment.parseZone(json.start).locale("ja");
  const end = moment.parseZone(json.end).locale("ja");
  const duration = moment.duration(json.duration);

  return new Program(
    json.id,
    json.service,
    json.channel || "",
    json.channel_jp,
    json.title,
    json.info,
    start,
    end,
    duration,
    json.is_movie,
    json.is_repeat,
    json.is_reserved,
    json.is_recorded
  );
}

interface Channel {
  name: string;
  nameJP: string;
  programs: Program[];
}

function fetchGuide() {
  return fetch("/api/guide.json")
    .then(res => res.json())
    .then(json =>
      json.map(
        (channel: any): Channel => {
          const programs = channel.programs.map((p: any) => jsonToProgram(p));
          return {
            name: channel.name,
            nameJP: channel.name_jp,
            programs: programs
          };
        }
      )
    );
}
function fetchReserved() {
  return fetch("/api/reserved.json")
    .then(res => res.json())
    .then(json => json.map((p: any) => jsonToProgram(p)));
}
export { IProgram, Program, jsonToProgram, fetchGuide, fetchReserved, Channel };
