import endent from 'endent';
import {
  createParser,
  ParsedEvent,
  ReconnectInterval,
} from 'eventsource-parser';
// import fetch from 'node-fetch';

const createPrompt = (inputCode: string) => {
  const data = (inputCode: string) => {
    return endent`${inputCode}`;
  };

  if (inputCode) {
    return data(inputCode);
  }
};

export const OpenAIStream = async (
  inputCode: string,
  model: string,
  key: string | undefined,
) => {
  const prompt = createPrompt(inputCode);

  const system = { role: 'system', content: prompt };

  const res = await fetch(`https://api.openai.com/v1/chat/completions`, {
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${key || process.env.NEXT_PUBLIC_OPENAI_API_KEY}`,
    },
    method: 'POST',
    body: JSON.stringify({
      model,
      messages: [system],
      temperature: 0,
      stream: true,
    }),
  });

  const encoder = new TextEncoder();
  const decoder = new TextDecoder();

  if (res.status !== 200) {
    const statusText = res.statusText;
    const result = await res.body?.getReader().read();
    throw new Error(
      `OpenAI API returned an error: ${
        decoder.decode(result?.value) || statusText
      }`,
    );
  }

  const stream = new ReadableStream({
    async start(controller) {
      const onParse = (event: ParsedEvent | ReconnectInterval) => {
        if (event.type === 'event') {
          const data = event.data;

          if (data === '[DONE]') {
            controller.close();
            return;
          }

          try {
            const json = JSON.parse(data);
            const text = json.choices[0].delta.content;
            const queue = encoder.encode(text);
            controller.enqueue(queue);
          } catch (e) {
            controller.error(e);
          }
        }
      };

      const parser = createParser(onParse);

      for await (const chunk of res.body as any) {
        parser.feed(decoder.decode(chunk));
      }
    },
  });

  return stream;
};

// export const OpenAIStream = async (
//   inputCode: string,
//   model: string,
//   key: string | undefined,
// ) => {
//   const encoder = new TextEncoder();
//   const decoder = new TextDecoder();

//   const prompt = createPrompt(inputCode);

//   console.log(prompt);

//   // SOLUCION
//   // var myHeaders = new Headers();
//   // myHeaders.append("Content-Type", "application/json");

//   // var raw = JSON.stringify({
//   //   "input": "quien es messi"
//   // });

//   // var requestOptions = {
//   //   method: 'POST',
//   //   headers: myHeaders,
//   //   body: raw,
//   //   redirect: 'follow'
//   // };

//   // fetch("http://127.0.0.1:9001/request/chat", requestOptions)
//   //   .then(response => response.text())
//   //   .then(result => console.log(result))
//   //   .catch(error => console.log('error', error));

//   // ORIGINAL
//   // const system = { role: 'system', content: prompt };

//   // var requestOptions = {
//   //   method: 'POST',
//   //   headers: {
//   //           'Content-Type': 'application/json',
//   //           Authorization: `Bearer ${key || process.env.NEXT_PUBLIC_OPENAI_API_KEY}`,
//   //         },
//   //   body: JSON.stringify({
//   //           model,
//   //           messages: [system],
//   //           temperature: 0,
//   //           stream: true,
//   //         }),
//   //   redirect: 'follow'
//   // };

//   // fetch("https://api.openai.com/v1/chat/completions", requestOptions)
//   //   .then(response => response.text())
//   //   .then(result => console.log(result))
//   //   .catch(error => console.log('error', error));
  
//   const res = await fetch('http://127.0.0.1:9001/request/chat', {
//     method: 'POST',
//     headers: {
//       'Content-Type': 'application/json'
//     },
//     body: JSON.stringify({ 
//       input: "quien es messi?"
//     }),
//     redirect: 'follow'
//   });
//   console.log("logro pasar el fetch");
//   // console.log(res);
//   // console.log(res.text());

//   // if (res.status !== 200) {
//   //   const statusText = res.statusText;
//   //   const result = await res.body?.getReader().read();
//   //   throw new Error(
//   //     `OpenAI API returned an error: ${
//   //       decoder.decode(result?.value) || statusText
//   //     }`,
//   //   );
//   // }

//   const stream = new ReadableStream({
//     async start(controller) {
//       const onParse = (event: ParsedEvent | ReconnectInterval) => {
//         if (event.type === 'event') {
//           const data = event.data;

//           if (data === '[DONE]') {
//             controller.close();
//             return;
//           }

//           try {
//             const json = JSON.parse(data);
//             // const text = json.choices[0].delta.content;
//             const text = json.choices[0].answer;
//             const queue = encoder.encode(text);
//             controller.enqueue(queue);
//           } catch (e) {
//             controller.error(e);
//           }
//         }
//       };
      
//       const parser = createParser(onParse);

//       for await (const chunk of res.body as any) {
//         parser.feed(decoder.decode(chunk));
//       }
//     },
//   });

//   return stream;
// };
