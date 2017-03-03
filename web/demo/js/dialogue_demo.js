var fukidashi, fukidashi2, mmd, koro;
enchant();

var MOTION_PATH = {
  boredom  : 'motion/mei_idle_boredom.vmd',
  think    : 'motion/mei_idle_think.vmd',
  yawn     : 'motion/mei_idle_yawn.vmd',
  laugh    : 'motion/mei_laugh.vmd',
  breath   : 'motion/mei_breath.vmd',
  left     : 'motion/mei_imagine_left_normal.vmd',
  right    : 'motion/mei_imagine_right_normal.vmd',
  greeting : 'motion/sd_mei_greeting.vmd'
};

// 音声認識
var recognition = new webkitSpeechRecognition();
recognition.continuous = true;
recognition.interimResults = true;
recognition.lang = "ja-JP";

// Speech Synthesis
var speechsynthesis = window.speechSynthesis;
var msg = new SpeechSynthesisUtterance();
msg.volume = 1.0;
msg.rate = 0.85;
msg.pitch = 0.85;
msg.lang = "ja-JP";
msg.voice = speechsynthesis.getVoices().filter(function(voice) { return voice.name == "Google 日本人"; })[0];
var last_speech_dt = 0;
var last_res = ""


function get_atango_response(final_transcript){
  koro = mmd.getModelRenderer("korokoro");
  document.getElementById("info").innerText = "へんじをかんがえてます...";

  var think = new MMD.Motion(MOTION_PATH['think']);
  think.load(function() {
    think.loop = true;
    koro.addModelMotion("think", think);
    koro.play("think");
  });

  console.log(final_transcript);
  httpObj = new XMLHttpRequest();
  function speech(httpObj){
    if ((httpObj.readyState == 4) && (httpObj.status == 200)){
      console.log(httpObj.responseText);

      fukidashi2 = create_fukidashi(httpObj.responseText, 100, 700, 'yellow');
      game.rootScene.addChild(fukidashi2);

      if (last_res != httpObj.responseText){
        msg.text = httpObj.responseText;
        speechsynthesis.speak(msg);
        cnt++;
        last_res = httpObj.responseText.replace(/ /g, '');
        last_speech_dt = new Date();
        last_speech_dt = last_speech_dt.getTime();
      }

      document.getElementById("utterance").innerText = cnt;
      document.getElementById("info").innerText = "もっとはなそう！";
      var yawn = new MMD.Motion(MOTION_PATH['yawn']);
      yawn.load(function() {
        yawn.loop = true;
        koro.addModelMotion("yawn", yawn);
        koro.play("yawn");
      });
    } else{
      var laugh = new MMD.Motion(MOTION_PATH['laugh']);
      laugh.load(function() {
        laugh.loop = true;
        koro.addModelMotion("laugh", laugh);
        koro.play("laugh");
      });
    }
  }
  httpObj.onreadystatechange = function(){speech(httpObj);};
  if (httpObj){
      url = window.location.origin+'/api/dialogue/?text='+final_transcript;
    httpObj.open("GET", url, true);
    httpObj.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    httpObj.send();
  }
}

recognition.onresult = function(event) {
  if (speechsynthesis.speaking){
    last_speech_dt = new Date();
    last_speech_dt = last_speech_dt.getTime();
    return;
  }
  now_dt = new Date();
  time_delta = now_dt.getTime() - last_speech_dt;
  if (time_delta < 3500){
    return;
  }

  var length = event.results.length;
  var intermediate_transcript ="";
  var final_transcript = "";
  if (length > 0) {
    for (var i = event.resultIndex; i < event.results.length; i++){
      var recogStr = event.results[i][0].transcript;
      intermediate_transcript += recogStr;
      remove_fukidashi();
      fukidashi = create_fukidashi(intermediate_transcript, 100, 10, 'white');
      game.rootScene.addChild(fukidashi);
      setTimeout(remove_fukidashi(), 5000);
      //認識の最終結果
      if (event.results[i].isFinal || i == event.results.length){
        if (recogStr == ' うー') {
            return;
        }
        final_transcript += recogStr
      }
    }
    if (final_transcript.length > 1 && final_transcript.replace(/ /g, '') != last_res){
      remove_fukidashi();
      fukidashi = create_fukidashi(final_transcript, 100, 10, 'white');
      game.rootScene.addChild(fukidashi);
      setTimeout(remove_fukidashi(), 5000);

      get_atango_response(final_transcript);
    }
    else {
      document.getElementById("info").innerText = "にんしきちゅう...";
      koro = mmd.getModelRenderer("korokoro");
      var think = new MMD.Motion(MOTION_PATH['think']);
      think.load(function() {
        think.loop = true;
      koro.addModelMotion("think", think);
        koro.play("think");
      });
    }
  }
};

recognition.onstart = function(event) {
  document.getElementById("info").innerText = "なにかはなそう！";
  koro = mmd.getModelRenderer("korokoro");
  var boredom = new MMD.Motion(MOTION_PATH['boredom']);
  boredom.load(function() {
      boredom.loop = true;
    koro.addModelMotion("boredom", boredom);
      koro.play("boredom");
  });
};

recognition.onspeechstart = function(event) {
  document.getElementById("info").innerText = "にんしきちゅう...";
  koro = mmd.getModelRenderer("korokoro");
    var think = new MMD.Motion(MOTION_PATH['think']);
    think.load(function() {
        think.loop = true;
      koro.addModelMotion("think", think);
        koro.play("think");
    });
};

recognition.onnomatch = function(){
  document.getElementById("info").innerText = "ききとれなかったよ！";
};

recognition.onerror = function(){
  document.getElementById("info").innerText = "エラー";
};

recognition.onend = function(){
  document.getElementById("info").innerText = "またはなそう？";
  recognition.start();
};
var cnt = 0;
recognition.start();

window.onload = function() {
  game = new Game(1000, 1000);
  game.onload = function() {
    var scene = new Scene3D();
  var camera = scene.getCamera();
  camera.y = 20;
  camera.z = 80;
  camera.centerY = 10;

    var canvas = document.getElementsByTagName('canvas')[0];
    mmd = new MMD(canvas, canvas.width, canvas.height);
    mmd.registerKeyListener(canvas);
    mmd.registerMouseListener(canvas);

    mmd.addModel("korokoro", new MMD.Model('model/korokoro', 'korokoro.pmd'));

    mmd.load(function() {
      var koro = mmd.getModelRenderer("korokoro");
      koro.translate(0, 6, 0.0);

      var greet = new MMD.Motion(MOTION_PATH['greeting']);
      greet.load(function() {
        greet.loop = false;
        koro.addModelMotion("greeting", greet);
        koro.play("greeting");
      });

      mmd.start();
      mmd.play();
    });
    game.rootScene.addChild(mmd);

    var oldX = 0;
    r = Math.PI / 2;

    game.rootScene.addEventListener('touchstart', function(e) {
        oldX = e.x;
    });
    game.rootScene.addEventListener('touchmove', function(e) {
      r += (e.x - oldX) / 100;
      camera.x = Math.cos(r) * 80;
      camera.z = Math.sin(r) * 80;
      oldX = e.x;
    });

    var label = new Label('0');
    label.font = '24px helvetica';
    label.color = '#fff';
    game.rootScene.addChild(label);
    var c = 0;
    setInterval(function() {
      label.text = c;
      c = 0;
    }, 1000);
    game.rootScene.addEventListener('enterframe', function(e) {
        c++;
    });
  };
  game.start(); //ゲーム開始
};


function remove_fukidashi(){
  if (fukidashi){
    fukidashi.remove();
    fukidashi = null;
  }
  if (fukidashi2){
    fukidashi2.remove();
    fukidashi2 = null;
  }
}
