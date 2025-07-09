pipeline {
    agent any

    environment {
        P4_CRED_ID = 'your-p4-credential-id'
        P4_STREAM = '//depot/stream/main'
        BASELINE_CL = '12345'  // ← ここを起点の changelist に設定
        SLACK_CHANNEL = '#your-channel'
    }

    triggers {
        pollSCM('H/5 * * * *')  // 5分おきにチェック
    }

    stages {
        stage('Check for New Changes') {
            steps {
                script {
                    // 指定チェンジリストより新しい変更を最大10件取得
                    def output = sh(
                        script: "p4 -ztag changes -m10 ${env.P4_STREAM}@${env.BASELINE_CL},now",
                        returnStdout: true
                    ).trim()

                    def newCLs = (output =~ /change (\d+)/).collect { it[1] }

                    if (newCLs.size() > 0) {
                        echo "New changelists found since ${env.BASELINE_CL}: ${newCLs.join(', ')}"

                        // 最新CLの詳細を取得して通知
                        def latestCL = newCLs[0]

                        def desc = sh(
                            script: "p4 describe -s ${latestCL}",
                            returnStdout: true
                        ).trim()

                        slackSend(
                            channel: env.SLACK_CHANNEL,
                            message: "*New Perforce Submit Detected!*\n" +
                                     "Stream: `${env.P4_STREAM}`\n" +
                                     "Changes since ${env.BASELINE_CL}: `${newCLs.join(', ')}`\n" +
                                     "Latest change:\n```" + desc + "```"
                        )
                    } else {
                        echo "No changes since CL ${env.BASELINE_CL}"
                    }
                }
            }
        }
    }
}
